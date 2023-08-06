import galpy.util.bovy_coords as gub
import numpy as np
import constants
from galpy.orbit import Orbit
from galpy.potential import MWPotential2014



class Star_Dyna:
    def __init__(self, ra, dec, dist, pmra, pmdec, RV, e_pmra=None, e_pmdec=None, e_dist=None, e_RV=None, p_pmradec=None):
        self.ra = ra
        self.dec = dec
        self.dist = dist
        self.pmra = pmra
        self.pmdec = pmdec
        self.RV = RV
        self.e_dist = e_dist
        self.e_pmra = e_pmra
        self.e_pmdec = e_pmdec
        self.e_RV = e_RV
        self.p_pmradec = p_pmradec

    def radec_to_lb(self, ra=None, dec=None, degree=True, external=False):
        if external:
            lb = gub.radec_to_lb(ra, dec, degree=degree)
            return lb[:,0], lb[:,1]
        else:
            ra = self.ra
            dec = self.dec
            lb = gub.radec_to_lb(ra, dec, degree=degree)
            self.glon = lb[:,0]
            self.glat = lb[:,1]

    def pmradec_to_pmllbb(self, ra=None, dec=None, pmra=None, pmdec=None, e_pmra=None, e_pmdec=None, external=False):
        if external:
            pmllbb = gub.pmrapmdec_to_pmllpmbb(pmra, pmdec, ra, dec, degree=True)
            return pmllbb[:,0], pmllbb[:,1]
        else:
            ra = self.ra
            dec = self.dec
            pmra = self.pmra
            pmdec = self.pmdec
            e_pmra = self.e_pmra
            e_pmdec = self.e_pmdec
            pmllbb = gub.pmrapmdec_to_pmllpmbb(pmra, pmdec, ra, dec, degree=True)
            self.pmll = pmllbb[:,0]
            self.pmbb = pmllbb[:,1]

    def vrpm_to_vxvyvz(self,rv=None, pmll=None, pmbb=None, ll=None, bb=None,
                       dist=None, external=False):
        if external:
            pass




def action_angle(ra=None, dec=None, dist=None, pmra=None, pmdec=None, rv=None,
                 X_sun=constants.X_sun, V_LSR=constants.V_LSR, U_sun=constants.U_sun,
                 V_sun=constants.V_sun, W_sun=constants.W_sun):
    """
    -----------------------------
    input:
    ra, dec in unit degree
    dist in unit kpc
    pm in unit mas/yr
    rv in unit km/s
    -----------------------------
    output:
    JRJPJZ: actions in shape of (N, 3), for JR, JPhi, JZ
    WRWPWT: frequence in shape of (N, 3), for wR, wPhi, wZ
    L_info: angular momentum in shape of (N, 5), for Lx, Ly, Lz, Lxy, Ltotal
    vrvtvz: velocities in cylindrical coordinates in shape of (N, 3), for VR, Vphi, VZ
    xyz_gc: positions in cartesian coordinates in shape of (N,3), for X, Y, Z relative to the Galactic center.
    """

    # convert ra dec to l b
    llbb = gub.radec_to_lb(ra, dec, degree=True)

    # centered at LSR, with galactic center at (X_sun,0,0)kpc
    xyz = gub.lbd_to_XYZ(llbb[:, 0], llbb[:, 1], dist, degree=True)

    # proper motion along l and b
    pmllbb = gub.pmrapmdec_to_pmllpmbb(pmra, pmdec, ra, dec, degree=True)

    # velocity relative to the Sun
    vxvyvz = gub.vrpmllpmbb_to_vxvyvz(rv, pmllbb[:, 0], pmllbb[:, 1], llbb[:, 0], llbb[:, 1], \
                                      dist, degree=True)

    vxvyvz_gc = np.zeros_like(vxvyvz)
    vxvyvz_gc[:, 0] = -(vxvyvz[:, 0] + U_sun)
    vxvyvz_gc[:, 1] = vxvyvz[:, 1] + V_sun + V_LSR
    vxvyvz_gc[:, 2] = vxvyvz[:, 2] + W_sun

    print(vxvyvz[0, 0] + U_sun, vxvyvz[0, 1] + V_LSR + V_sun, vxvyvz[0, 2] + W_sun, '-------------gub')
    # angular momentum
    Lx = (xyz[:, 1]) * (vxvyvz[:, 2] + W_sun) - xyz[:, 2] * (vxvyvz[:, 1] + V_LSR + V_sun)
    Ly = xyz[:, 2] * (-vxvyvz[:, 0] - U_sun) - (X_sun - xyz[:, 0]) * (vxvyvz[:, 2] + W_sun)
    Lz = (X_sun - xyz[:, 0]) * (vxvyvz[:, 1] + V_sun + V_LSR) - xyz[:, 1] * (-vxvyvz[:, 0] - U_sun)
    Lxy = np.sqrt(Lx ** 2 + Ly ** 2)  # angular momentum in perpendicular
    LT = np.sqrt(Lx ** 2 + Ly ** 2 + Lz ** 2)  # total angular momentum
    L_info = np.zeros((len(Lz), 5))
    L_info[:, 0] = Lx
    L_info[:, 1] = Ly
    L_info[:, 2] = Lz
    L_info[:, 3] = Lxy
    L_info[:, 4] = LT

    # here the sun's uvw in GC frame, XYZ in gc frame, UVW in LSR frame
    vrvtvz = gub.vxvyvz_to_galcencyl(vxvyvz[:, 0], vxvyvz[:, 1], vxvyvz[:, 2], \
                                     X_sun - xyz[:, 0], xyz[:, 1], xyz[:, 2], [U_sun * (-1), V_LSR + V_sun, W_sun])
    xyz_gc = xyz * 1.0
    xyz_gc[:, 0] = X_sun - xyz[:, 0]

    # cylindrical coordinates
    Phi_xy = np.arctan2(xyz_gc[:, 1], xyz_gc[:, 0]) * 180 / np.pi
    R = np.sqrt((X_sun - xyz[:, 0]) ** 2 + xyz[:, 1] ** 2)

    JRJPJZ = np.zeros((len(ra), 3))  # [:,0] for JR, [:,1] for JPhi, also Lz, [:,2] JZ
    WRWPWT = np.zeros((len(ra), 3))  # [:,0] for wR, [:,1] for wPhi,  [:,2] wZ

    JRJPJZo = np.zeros((len(ra), 3))  # [:,0] for JR, [:,1] for JPhi, also Lz, [:,2] JZ
    WRWPWTo = np.zeros((len(ra), 3))  # [:,0] for wR, [:,1] for wPhi,  [:,2] wZ

    Zmax = np.zeros((len(ra)))
    Rg = np.zeros((len(ra)))
    Rperi = np.zeros((len(ra)))
    Rapo = np.zeros((len(ra)))
    ecc = np.zeros((len(ra)))
    for i in range(len(ra)):
        o = Orbit(vxvv=[R[i] / X_sun, vrvtvz[i, 0] / V_LSR, vrvtvz[i, 1] / V_LSR, \
                        xyz_gc[i, 2] / X_sun, vrvtvz[i, 2] / V_LSR, Phi_xy[i]], ro=X_sun, vo=V_LSR)
        JRJPJZo[i, 0], JRJPJZo[i, 1], JRJPJZo[i, 2] = o.jr(pot=MWPotential2014), o.jp(pot=MWPotential2014), o.jz(
            pot=MWPotential2014)
        WRWPWTo[i, 0], WRWPWTo[i, 1], WRWPWTo[i, 2], = o.wr(pot=MWPotential2014), o.wp(pot=MWPotential2014), o.wz(
            pot=MWPotential2014)
        Zmax[i] = o.zmax(pot=MWPotential2014, analytic=True)
        Rg[i] = o.rguiding(pot=MWPotential2014)
        Rperi[i] = o.rperi(pot=MWPotential2014, analytic=True)
        Rapo[i] = o.rap(pot=MWPotential2014, analytic=True)
        ecc[i] = o.e(pot=MWPotential2014, analytic=True)
    return L_info, vrvtvz, xyz_gc, JRJPJZo, WRWPWTo, Zmax, Rg, Rperi, Rapo, ecc
