import numpy as np
import math
import pandas

def cosd(x): return np.cos(np.deg2rad(x))
def sind(x): return np.sin(np.deg2rad(x))
def tand(x): return np.tan(np.deg2rad(x))
def atand(x):return np.rad2deg(np.arctan(x))


#DATA OLD
Lh = 9000 #D h
ipn = 3 #DS
ic = 7.5 #DS
nsp = 1440 #DS rpm
N0 = 2.2 #DS kW


# Stal chromowo-manganowo-niklowa
Zgo = 440
Zgj = 690
HB = 228
Re = 750
Rm = 1050

alphan = 20
betaz = 10
yn =1

mn = 4
psi = 10

Cc = 1
Xzj = 2
Xzo = 2.5

kgj = Cc*Zgj/Xzj
kgo = Cc*Zgo/Xzo #MPa

kg = min(kgj,kgo)

n1 = nsp/ipn

M0 = (9550*(10**3))*N0/n1

alphat = atand((tand(alphan))/cosd(betaz))
yt = yn * cosd(betaz)
Zgb =yt * (2 / sind(alphat)**2)
Z1 = np.ceil(Zgb)
Z1z = np.ceil(Z1/(cosd(betaz)**3))
iz = ic/ipn
Z2 = np.ceil(Z1z *iz)


d1 = (mn*Z1z)/cosd(betaz)
v = (math.pi * d1 * n1)/60000
Cd = 1 + (math.sqrt(v)/7)

C1 = (1 / (2 * np.pi)) * np.sqrt(((1 + (2 * cosd(betaz)) / Z1z)**2 * (1 + (tand(alphan)**2 / cosd(betaz)**2))) - 1)
C2 = (1 / (2 * np.pi)) * np.sqrt(((1 + (2 * cosd(betaz)) / Z2)**2 * (1 + (tand(alphan)**2 / cosd(betaz)**2))) - 1)
C3 = ((Z1z + Z2) * tand(alphan)) / (2 * np.pi * cosd(betaz))
ealpha = (Z1z*C1) + (Z2*C2) - C3
ebeta = np.ceil(psi * (sind(betaz)/np.pi))
psip = (ebeta*np.pi)/sind(betaz)
egamma = ealpha + psip
lambda_zast = 6.69
Cbeta = 1.4
Cp = 1.75
mg = np.cbrt((Cp * Cd * 2 * 9550 * 1000 * N0 * cosd(betaz)) / (psi * lambda_zast * Cbeta * Z1z * kg* n1))

Ft = 2*M0/d1
Fr = Ft * (tand(alphan)/cosd(betaz) )
Fa = Ft * tand(betaz)
d2 = (Z2*mn)/cosd(betaz)
ha2 = mn
ha1 = ha2


da1 = d1+2*ha1
da2 = d2+2*ha2
df1 = d1-2*ha1
df2 = d2-2*ha2

b = mg * psip

Ps = (2*9550e3*N0)/(d1*n1)



kH = 482.05
E = 2.06e5        # MPa (stal)
Cma = np.sqrt( (1.4 * E * E) / ((E + E) * np.sin(np.deg2rad(2*alphan))) )
M_nH = np.cbrt( ((Cma) * 2 * 9550 * 1000 * N0 * (cosd(betaz)**2)) / (psip * ealpha * Z1z**2 * n1 * kH) )*(1+(Z1z/Z2))

mnf = np.ceil(max(M_nH,mg))
#z tabelki o pasach
zp = 4 #liczba pasow
f = 10 #tabelka
e = 15 # tabelka
bp = 2*f+((zp-1)*e)
bz = mnf * psip
wa1 = (bp/2) + 15 + (25/2)
wa2 = (25/2) + 15 + (bz/2)
wa = wa1+wa2

Qz = 102.78
Qy = 771.13
Dp = 213
dp = 71

Rbx = -1*Fa
Rdy = ((-1*Qy*wa1)-(Fr*wa2)-(Fa*(dp/2)))/(2*wa2)
Rby = (-1*Rdy)+Qy-Fr

Rdz = ((Qz*wa1)+(Ft*wa2))/(2*wa2)
Rbz = Ft - Qz - Rdz

# Płaszczyzna Y (pionowa)
Mg1   = -Qy * wa1
Mg1z  =  Qz * wa1

Mg2  = (-Qy * (wa1+wa2)) + (Rby * ((wa1+wa2)-wa1))   # FIX: dodane *(wa2)
Mg2z = ( Qz * (wa1+wa2)) + (Rbz * ((wa1+wa2)-wa1))

Mg3  = Rdy * wa2
Mg3z = Rdz * wa2

n1sk = n1/3
Ms = 9550*n1sk*(N0/10**3)

MgI   = 0.0
MgII  = np.sqrt(Mg1**2  + Mg1z**2)
MgIII = np.sqrt(Mg2**2 + Mg2z**2)
MgIV  = np.sqrt(Mg3**2  + Mg3z**2)
MgV   = 0.0

Mz2 = np.sqrt((MgII)**2+((3/16)*(Ms**2)))
Mz3 = np.sqrt((MgIII)**2+((3/16)*(Ms**2)))
Mz4 = np.sqrt((MgIII)**2+((3/16)*(Ms**2)))


WRm = 570
Wxz = 4

wksj = 0.56*WRm/Wxz
wkgo = 0.42*WRm/Wxz

Wk = wkgo

Wd1 = np.cbrt((16*Mz2)/(np.pi*Wk))
Wd2 = np.cbrt((16*Mz3)/(np.pi*Wk))
Wd3 = np.cbrt((16*Mz4)/(np.pi*Wk))







print(f"b {b}")
print(f"Z2 = {Z2}")
print(f"Test {Cma}")
print(f"N0 = {N0}")
print(f"psip = {psip}")
print(f"ealpha = {ealpha}")
print(f"n1 = {n1}")
print(f"Mh {M_nH}")
print(f"mg {mg}")
print(f"z1z = {Z1z}")
print(f"d1 {d1}")
print(f"mnf = {mnf}")
print(f"d2 {d2}")
print(f"a1 {wa1}")
print(f"a2 {wa2}")
print(f"n1sk {n1sk}")
print(f"bp {bp}")
print(f"bz = {bz}")
print(f"MgI = {MgI}")
print(f"MgII = {MgII}")
print(f"MgIII = {MgIII}")
print(f"MgIV = {MgIV}")
print(f"Mg1 {Mg1}")
print(f"Mg2 {Mg2}")
print(f"Mg3 {Mg3}")
print(f"Ms {Ms}")
print(f"Wd1 = {Wd1}")
print(f"Wd2 = {Wd2}")
print(f"Wd3 = {Wd3}")