import numpy as np
import math

# ==============================================================================
# FUNKCJE POMOCNICZE
# ==============================================================================
def cosd(x): return np.cos(np.deg2rad(x))
def sind(x): return np.sin(np.deg2rad(x))
def tand(x): return np.tan(np.deg2rad(x))
def atand(x): return np.rad2deg(np.arctan(x))

# ==============================================================================
# SEKCJA 1: DANE WEJŚCIOWE I STAŁE MATERIAŁOWE
# ==============================================================================
# Dane wyjściowe układu
N_wyj = 1.51       # Moc wyjściowa na wale roboczym [kW]
K = 1.36           # Współczynnik bezpieczeństwa / przeciążenia
n2 = 192           # Prędkość obrotowa wału wyjściowego [obr/min]
Lh = 9000          # Wymagana trwałość godzinowa [h]

# Sprawności poszczególnych węzłów i elementów
eta_p = 0.96       # Sprawność przekładni pasowej
eta_t = 0.995      # Sprawność pary łożysk (wzór uwzględnia eta_t ** 2)
eta_z = 0.98       # Sprawność przekładni zębatej

# Dane silnika elektrycznego
n_s_prime = 1440   # Rzeczywiste obroty silnika [obr/min]

# Dane materiałowe koła zębatego (Stal chromowo-manganowo-niklowa)
Zgo = 440          # Wytrzymałość zmęczeniowa na zginanie przy obciążeniu obustronnym [MPa]
Zgj = 690          # Wytrzymałość zmęczeniowa na zginanie przy obciążeniu jednostronnym [MPa]
HB = 228           # Twardość Brinella
Re = 750           # Granica plastyczności [MPa]
Rm = 1050          # Wytrzymałość na rozciąganie [MPa]

# Parametry geometryczne uzębienia (wstępne)
alphan = 20        # Nominalny kąt przyporu [stopnie]
betaz = 10         # Kąt pochylenia linii zęba [stopnie]
yn = 1             # Współczynnik wysokości zęba
mn = 4             # Moduł nominalny [mm] (wstępny)
psi = 10           # Współczynnik szerokości wieńca

# Współczynniki bezpieczeństwa i poprawkowe dla kół zębatych
Cc = 1             # Współczynnik trwałościowy
Xzj = 2            # Współczynnik bezpieczeństwa dla naprężeń jednostronnych
Xzo = 2.5          # Współczynnik bezpieczeństwa dla naprężeń obustronnych
kH = 482.05        # Dopuszczalne naciski kontaktowe [MPa]
E = 2.06e5         # Moduł Younga dla stali [MPa]

# Dane geometryczne przekładni pasowej (do wyznaczenia szerokości i sił)
zp = 4             # Liczba pasów klinowych
f = 10             # Odległość boczna pasa od krawędzi koła [mm] (z tabeli)
e = 15             # Rozstaw rowków pasowych [mm] (z tabeli)
Dp = 213           # Średnica koła pasowego dużego [mm]
dp = 71            # Średnica koła pasowego małego [mm]

# Obciążenia od przekładni pasowej działające na wał (składowe siły naciągu)
Qz = 102.78        # Składowa pozioma siły naciągu pasów [N]
Qy = 771.13        # Składowa pionowa siły naciągu pasów [N]

# Dane do obliczeń wytrzymałościowych wału
WRm = 570          # Wytrzymałość rdzenia wału [MPa]
Wxz = 4            # Współczynnik bezpieczeństwa dla wału

# ==============================================================================
# SEKCJA 2: DOBÓR SILNIKA I KINEMATYKA UKŁADU
# ==============================================================================
# Obliczenie całkowitej sprawności i mocy silnika
eta_c = eta_p * (eta_t ** 2) * eta_z
N0 = (K * N_wyj) / eta_c

# Obliczenie przełożeń
i_c = n_s_prime / n2
i_p = i_c ** 0.5
i_pn = math.ceil(i_p)  # Zaokrąglenie w górę przełożenia pasowego

# Prędkość obrotowa wału szybkiegu (wejściowego przekładni zębatej)
n1 = n_s_prime / i_pn
M0 = (9550 * (10**3)) * N0 / n1

# ==============================================================================
# SEKCJA 3: OBLICZENIA PRZEKŁADNI PASOWEJ (TYP A)
# ==============================================================================
Kt = 1.0           # Współczynnik pracy
N1 = 0.68          # Moc przenoszona przez jeden pas [kW]
Lpn = 1032         # Długość pasa z katalogu [mm]
k_l = 0.89         # Współczynnik długości pasa
kφ = 0.93          # Współczynnik kąta opasania

D_p_calc = dp * i_pn  # Średnica koła napędzanego

# Geometria napędu pasowego
p_belt = 0.25 * Lpn - 0.393 * (D_p_calc + dp)
q_belt = 0.125 * (D_p_calc - dp)**2
A_belt = p_belt + math.sqrt(p_belt**2 - q_belt)
phi_belt = (D_p_calc - dp) / A_belt

# Wyznaczenie liczby pasów
Z_belt = (N0 * Kt) / (N1 * kφ * k_l)
Z_up = math.ceil(Z_belt)

# ==============================================================================
# SEKCJA 4: GEOMETRIA I WYTRZYMAŁOŚĆ PRZEKŁADNI ZĘBATEJ
# ==============================================================================
# Naprężenia dopuszczalne na zginanie
kgj = Cc * Zgj / Xzj
kgo = Cc * Zgo / Xzo
kg = min(kgj, kgo)

# Parametry zazębienia
alphat = atand((tand(alphan)) / cosd(betaz))
yt = yn * cosd(betaz)
Zgb = yt * (2 / sind(alphat)**2)
Z1 = np.ceil(Zgb)
Z1z = np.ceil(Z1 / (cosd(betaz)**3))
iz = 7.5 / 3  # Przełożenie przekładni zębatej (ic / ipn)
Z2 = np.ceil(Z1z * iz)

# Średnice i prędkość obwodowa
d1 = (mn * Z1z) / cosd(betaz)
v = (math.pi * d1 * n1) / 60000
Cd = 1 + (math.sqrt(v) / 7)

# Współczynniki pokrycia (wskaźniki zazębienia)
C1 = (1 / (2 * np.pi)) * np.sqrt(((1 + (2 * cosd(betaz)) / Z1z)**2 * (1 + (tand(alphan)**2 / cosd(betaz)**2))) - 1)
C2 = (1 / (2 * np.pi)) * np.sqrt(((1 + (2 * cosd(betaz)) / Z2)**2 * (1 + (tand(alphan)**2 / cosd(betaz)**2))) - 1)
C3 = ((Z1z + Z2) * tand(alphan)) / (2 * np.pi * cosd(betaz))
ealpha = (Z1z * C1) + (Z2 * C2) - C3
ebeta = np.ceil(psi * (sind(betaz) / np.pi))
psip = (ebeta * np.pi) / sind(betaz)
egamma = ealpha + psip

# Weryfikacja modułu ze względu na zginanie (mg)
lambda_zast = 6.69
Cbeta = 1.4
Cp = 1.75
mg = np.cbrt((Cp * Cd * 2 * 9550 * 1000 * N0 * cosd(betaz)) / (psi * lambda_zast * Cbeta * Z1z * kg * n1))

# Siły międzyzębne
Ft = 2 * M0 / d1
Fr = Ft * (tand(alphan) / cosd(betaz))
Fa = Ft * tand(betaz)

# Pozostałe wymiary kół zębatych
d2 = (Z2 * mn) / cosd(betaz)
ha2 = mn
ha1 = ha2
da1 = d1 + 2 * ha1
da2 = d2 + 2 * ha2
df1 = d1 - 2 * ha1
df2 = d2 - 2 * ha2
b = mg * psip
Ps = (2 * 9550e3 * N0) / (d1 * n1)

# Weryfikacja modułu ze względu na naciski powierzchniowe (M_nH)
Cma = np.sqrt((1.4 * E * E) / ((E + E) * np.sin(np.deg2rad(2 * alphan))))

M_nH = np.cbrt( ((Cma**2) * 2 * 9550 * 1000 * N0 * (cosd(betaz)**2)) / (psip * ealpha * Z1z**2 * n1 * (kH**2)) ) * (1 + (Z1z / Z2))

# Ostateczny dobór modułu normalnego
mnf = np.ceil(max(M_nH, mg))

# ==============================================================================
# SEKCJA 5: REAKCJE PODPOROWE I MOMENTY NA WALE
# ==============================================================================
# Szerokości gabarytowe elementów wału
bp = 2 * f + ((zp - 1) * e)
bz = mnf * psip
wa1 = (bp / 2) + 15 + (25 / 2)
wa2 = (25 / 2) + 15 + (bz / 2)
wa = wa1 + wa2

# Reakcje w podporach (łożyskach)
Rbx = -1 * Fa
Rdy = ((-1 * Qy * wa1) - (Fr * wa2) - (Fa * (d1 / 2))) / (2 * wa2)
Rby = (-1 * Rdy) + Qy - Fr

Rdz = ((Qz * wa1) + (Ft * wa2)) / (2 * wa2)
Rbz = Ft - Qz - Rdz

# Momenty gnące składowe w charakterystycznych punktach wału
Mg1 = -Qy * wa1
Mg1z = Qz * wa1

Mg2 = (-Qy * (wa1 + wa2)) + (Rby * ((wa1 + wa2) - wa1))
Mg2z = (Qz * (wa1 + wa2)) + (Rbz * ((wa1 + wa2) - wa1))

Mg3 = Rdy * wa2
Mg3z = Rdz * wa2

# Obliczenie momentu skręcającego wał szybki
n1sk = n1 / 3
Ms = 9550 * n1sk * (N0 / 10**3)

# Wypadkowe momenty gnące w przekrojach (I - V)
MgI = 0.0
MgII = np.sqrt(Mg1**2 + Mg1z**2)
MgIII = np.sqrt(Mg2**2 + Mg2z**2)
MgIV = np.sqrt(Mg3**2 + Mg3z**2)
MgV = 0.0

# Momenty zredukowane (zastępcze)
Mz2 = np.sqrt((MgII)**2 + ((3 / 16) * (Ms**2)))
Mz3 = np.sqrt((MgIII)**2 + ((3 / 16) * (Ms**2)))
Mz4 = np.sqrt((MgIII)**2 + ((3 / 16) * (Ms**2)))




# ==============================================================================
# SEKCJA 6: OBLICZENIA WYTRZYMAŁOŚCIOWE WAŁU (ŚREDNICE)
# ==============================================================================
wksj = 0.56 * WRm / Wxz
wkgo = 0.42 * WRm / Wxz
Wk = wkgo  #dominacja genetyczna Mg nad Ms

# Minimalne obliczeniowe średnice wału w poszczególnych przekrojach [mm]
Wd1m = np.cbrt((16 * Mz2) / (np.pi * Wk))
Wd2m = np.cbrt((16 * Mz3) / (np.pi * Wk))
Wd3m = np.cbrt((16 * Mz4) / (np.pi * Wk))

# wpust z tabelki
bw = 6
hw = 6
t1 = 3.5
t2 = 2.8
zw = 6
wc = 1

#lozyska
Pd = np.sqrt(Rdy**2+Rdz**2)
Cd = Pd/10 * np.cbrt(Lh*n1sk/16666) #daN


#srednice walu
Wd1 = 20
Wd2 = np.floor(1.2*Wd1)
Wd3 = 19
Wd4 = Wd1
Wd5 = 20
Wd6 = 25
Wd7 = Wd3
Wd8 = Wd5
Wd9 = Wd8 - 2*wc
Wd10 = Wd5
Wd11 = Wd6

#Warunki wpustu
Pp = 2*M0/Wd1
wpd = 130
lw = 4*M0/(Wd1 * hw * wpd)
Ap = hw/2*lw
l0 = lw+bw
l0n = 18



# ==============================================================================
# SEKCJA F: WYDRUK WYNIKÓW (PRINT)
# ==============================================================================
print("=======================================================================")
print("WYNIKI OBLICZEŃ KINEMATYCZNYCH I SILNIKA")
print("=======================================================================")
print(f"Całkowita sprawność układu (eta_c)      : {eta_c:.4f}")
print(f"Obliczeniowa moc silnika (N0)           : {N0:.3f} kW")
print(f"Teoretyczne przełożenie całkowite (i_c)  : {i_c:.3f}")
print(f"Teoretyczne przełożenie pasowe (i_p)    : {i_p:.3f}")
print(f"Znormalizowane przełożenie pasowe (i_pn): {i_pn}")
print(f"Prędkość obrotowa wału 1 (n1)           : {n1:.2f} obr/min")
print(f"Moment skrętny nominalny silnika (M0)   : {M0:.2f} Nmm")

print("\n=======================================================================")
print("WYNIKI OBLICZEŃ PRZEKŁADNIE PASOWEJ")
print("=======================================================================")
print(f"Obliczona odległość osi pasów (A_belt)   : {A_belt:.2f} mm")
print(f"Kąt pomocniczy opasania (phi_belt)      : {phi_belt:.4f} rad")
print(f"Obliczeniowa liczba pasów (Z_belt)      : {Z_belt:.2f}")
print(f"Przyjęta liczba pasów (Z_up)            : {Z_up}")
print(f"Szerokość koła pasowego (bp)            : {bp:.2f} mm")

print("\n=======================================================================")
print("WYNIKI OBLICZEŃ GEOMETRII I SIŁ PRZEKŁADNI ZĘBATEJ")
print("=======================================================================")
print(f"Wytrzymałość dopuszczalna (kg)          : {kg:.2f} MPa")
print(f"Kąt przyporu w płaszczyźnie czołowej (alphat): {alphat:.2f}°")
print(f"Liczba zębów zastępczych koła 1 (Z1z)   : {Z1z}")
print(f"Liczba zębów koła 2 (Z2)                : {Z2}")
print(f"Średnica podziałowa koła 1 (d1)         : {d1:.2f} mm")
print(f"Średnica podziałowa koła 2 (d2)         : {d2:.2f} mm")
print(f"Średnice wierzchołkowe (da1 / da2)      : {da1:.2f} mm / {da2:.2f} mm")
print(f"Średnice stóp (df1 / df2)               : {df1:.2f} mm / {df2:.2f} mm")
print(f"Prędkość obwodowa koła (v)              : {v:.2f} m/s")
print(f"Współczynnik dynamiczny (Cd)            : {Cd:.4f}")
print(f"Wskaźnik pokrycia profilu (ealpha)      : {ealpha:.4f}")
print(f"Zastępcza szerokość poosiowa (psip)     : {psip:.2f}")
print(f"Moduł obliczony na zginanie (mg)        : {mg:.4f} mm")
print(f"Moduł obliczony na nacisk (M_nH)        : {M_nH:.4f} mm")
print(f"Ostateczny moduł znormalizowany (mnf)   : {mnf} mm")
print(f"Szerokość wieńca zębatego (bz)          : {bz:.2f} mm")
print(f"Szerokość obliczeniowa b (mg * psip)    : {b:.2f} mm")
print(f"Siła obwodowa (Ft)                      : {Ft:.2f} N")
print(f"Siła promieniowa (Fr)                   : {Fr:.2f} N")
print(f"Siła osiowa (Fa)                        : {Fa:.2f} N")

print("\n=======================================================================")
print("REAKCJE PODPOROWE I GEOMETRIA WAŁU")
print("=======================================================================")
print(f"Rozstaw wału - odcinek wa1              : {wa1:.2f} mm")
print(f"Rozstaw wału - odcinek wa2              : {wa2:.2f} mm")
print(f"Całkowita długość wału pomocnicza (wa)  : {wa:.2f} mm")
print(f"Reakcja Rbx                             : {Rbx:.2f} N")
print(f"Reakcja Rby                             : {Rby:.2f} N")
print(f"Reakcja Rbz                             : {Rbz:.2f} N")
print(f"Reakcja Rdy                             : {Rdy:.2f} N")
print(f"Reakcja Rdz                             : {Rdz:.2f} N")

print("\n=======================================================================")
print("MOMENTY GNĄCE I SKRĘCAJĄCE W PRZEKROJACH")
print("=======================================================================")
print(f"Składowe momentu gnącego Mg1 / Mg1z     : {Mg1:.2f} Nmm / {Mg1z:.2f} Nmm")
print(f"Składowe momentu gnącego Mg2 / Mg2z     : {Mg2:.2f} Nmm / {Mg2z:.2f} Nmm")
print(f"Składowe momentu gnącego Mg3 / Mg3z     : {Mg3:.2f} Nmm / {Mg3z:.2f} Nmm")
print(f"Moment skręcający wału (Ms)             : {Ms:.2f} Nmm")
print(f"Wypadkowy moment gnący MgII             : {MgII:.2f} Nmm")
print(f"Wypadkowy moment gnący MgIII            : {MgIII:.2f} Nmm")
print(f"Wypadkowy moment gnący MgIV             : {MgIV:.2f} Nmm")
print(f"Moment zredukowany Mz2 (przekrój II)    : {Mz2:.2f} Nmm")
print(f"Moment zredukowany Mz3 (przekrój III)   : {Mz3:.2f} Nmm")
print(f"Moment zredukowany Mz4 (przekrój IV)    : {Mz4:.2f} Nmm")

print("\n=======================================================================")
print("OBLICZENIOWE MINIMALNE ŚREDNICE WAŁU")
print("=======================================================================")
print(f"Dopuszczalne naprężenie wału Wk (wkgo)  : {Wk:.2f} MPa")
print(f"Minimalna średnica wału Wd1             : {Wd1m:.2f} mm")
print(f"Minimalna średnica wału Wd2             : {Wd2m:.2f} mm")
print(f"Minimalna średnica wału Wd3             : {Wd3m:.2f} mm")
print(f"Srednica d1                             : {Wd1:.2f} mm")
print(f"Srednica d2                             : {Wd2:.2f} mm")
print(f"Srednica d3                             : {Wd3:.2f} mm")
print("=======================================================================")

print("\n=======================================================================")
print("OBLICZENIA DO LOZYSK")
print("=======================================================================")
print(f"Pd                                      : {Pd:.2f} N")
print(f"Cd                                      : {Cd:.2f} daN")
print(f"przyjete lozysko 6204"                                     )
print("=======================================================================")
print("\n=======================================================================")
print("OBLICZENIA Wpustu")
print("=======================================================================")
print(f"h                                       : {hw:.2f} N")
print(f"b                                       : {bw:.2f} daN")
print(f"lw                                      : {lw}     ")
print(f"l0                                      : {l0:.2f} ")
print("=======================================================================")