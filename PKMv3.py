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
psi_m = 10         # Współczynnik szerokości wieńca względem modułu (b/m_n) - POPRAWKA

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

# Moment obrotowy na wału szybkoobrotowym [Nmm] (9550 * 1000 daje Nmm)
M0 = (9550 * 1000 * N0) / n1

# ==============================================================================
# SEKCJA 3: OBLICZENIA PRZEKŁADNI PASOWEJ (TYP A)
# ==============================================================================
Kt = 1.0           # Współczynnik pracy
N1 = 0.68          # Moc przenoszona przez jeden pas [kW]
Lpn = 1032         # Długość pasa z katalogu [mm]
k_l = 0.89         # Współczynnik długości pasa
k_phi = 0.93       # Współczynnik kąta opasania

D_p_calc = dp * i_pn  # Średnica koła napędzanego [mm]

# Geometria napędu pasowego
p_belt = 0.25 * Lpn - 0.393 * (D_p_calc + dp)
q_belt = 0.125 * (D_p_calc - dp)**2
A_belt = p_belt + math.sqrt(p_belt**2 - q_belt)
phi_belt = (D_p_calc - dp) / A_belt # Sinus połowy kąta opasania

# Wyznaczenie liczby pasów
Z_belt = (N0 * Kt) / (N1 * k_phi * k_l)
Z_up = math.ceil(Z_belt)

# ==============================================================================
# SEKCJA 4: GEOMETRIA I WYTRZYMAŁOŚĆ PRZEKŁADNI ZĘBATEJ
# ==============================================================================
# Naprężenia dopuszczalne na zginanie [MPa]
kgj = Cc * Zgj / Xzj
kgo = Cc * Zgo / Xzo
kg = min(kgj, kgo)

# Parametry zazębienia
alphat = atand(tand(alphan) / cosd(betaz)) # Kąt przyporu w płaszczyźnie czołowej
yt = yn * cosd(betaz)
Zgb = yt * (2 / sind(alphat)**2) # Minimalna liczba zębów zastępczych

# POPRAWIONA LOGIKA OBLICZANIA ZĘBÓW
Z1 = int(np.ceil(Zgb * cosd(betaz)**3)) # Rzeczywista minimalna liczba zębów koła 1
Zv1 = Z1 / (cosd(betaz)**3)             # Zastępcza liczba zębów koła 1
iz = i_c / i_pn                          # Rzeczywiste przełożenie zębate (zamiast 7.5/3)
Z2 = int(np.ceil(Z1 * iz))               # Rzeczywista liczba zębów koła 2
Zv2 = Z2 / (cosd(betaz)**3)              # Zastępcza liczba zębów koła 2

# Średnice i prędkość obwodowa
d1 = (mn * Z1) / cosd(betaz)
v = (math.pi * d1 * n1) / 60000 # [m/s]
Cd = 1 + (math.sqrt(v) / 7)    # Współczynnik dynamiczny

# Współczynniki pokrycia (wskaźniki zazębienia)
C1 = (1 / (2 * np.pi)) * np.sqrt(((1 + (2 * cosd(betaz)) / Zv1)**2 * (1 + (tand(alphan)**2 / cosd(betaz)**2))) - 1)
C2 = (1 / (2 * np.pi)) * np.sqrt(((1 + (2 * cosd(betaz)) / Zv2)**2 * (1 + (tand(alphan)**2 / cosd(betaz)**2))) - 1)
C3 = ((Zv1 + Zv2) * tand(alphan)) / (2 * np.pi * cosd(betaz))
ealpha = (Zv1 * C1) + (Zv2 * C2) - C3
ebeta = np.ceil(psi_m * (sind(betaz) / np.pi)) # Poprawka: psi_m zamiast psi
psip = (ebeta * np.pi) / sind(betaz)           # Przyjęta szerokość względem modułu
egamma = ealpha + ebeta

# Weryfikacja modułu ze względu na zginanie (mg) [mm]
lambda_zast = 6.69
Cbeta = 1.4
Cp = 1.75
mg = np.cbrt((Cp * Cd * 2 * 9550 * 1000 * N0 * cosd(betaz)) / (psip * lambda_zast * Cbeta * Z1 * kg * n1))

# Siły międzyzębowe [N]
Ft = 2 * M0 / d1
Fr = Ft * (tand(alphan) / cosd(betaz))
Fa = Ft * tand(betaz)

# Pozostałe wymiary kół zębatych [mm]
d2 = (Z2 * mn) / cosd(betaz)
ha = mn
da1 = d1 + 2 * ha
da2 = d2 + 2 * ha
df1 = d1 - 2.5 * mn  # Poprawka: standardowy współczynnik głębokości stopy 1.25 (2*1.25 = 2.5)
df2 = d2 - 2.5 * mn
bz = mg * psip

# Weryfikacja modułu ze względu na naciski powierzchniowe (M_nH) [mm]
# POPRAWIONY WZÓR NA WSPÓŁCZYNNIK MATERIAŁOWY Z_E (dla stali-stal, nu=0.3)
Z_E = np.sqrt(E / (2 * np.pi * (1 - 0.3**2)))

M_nH = np.cbrt( ((Z_E**2) * 2 * 9550 * 1000 * N0 * (cosd(betaz)**2)) / (psip * ealpha * Z1**2 * n1 * (kH**2)) ) * (1 + (1 / iz))

# Ostateczny dobór modułu normalnego
mnf = int(np.ceil(max(M_nH, mg)))

# ==============================================================================
# SEKCJA 5: REAKCJE PODPOROWE I MOMENTY NA WALE
# ==============================================================================
# Szerokości gabarytowe elementów wału [mm]
bp = 2 * f + ((zp - 1) * e)
bz = mnf * psip
wa1 = (bp / 2) + 15 + (25 / 2)
wa2 = (25 / 2) + 15 + (bz / 2)
wa = wa1 + wa2

# Reakcje w podporach (łożyskach) [N]
Rbx = -1 * Fa
Rdy = ((-1 * Qy * wa1) - (Fr * wa2) - (Fa * (d1 / 2))) / (2 * wa2)
Rby = (-1 * Rdy) + Qy - Fr
Rdz = ((Qz * wa1) + (Ft * wa2)) / (2 * wa2)
Rbz = Ft - Qz - Rdz

# Momenty gnące składowe w charakterystycznych punktach wału [Nmm]
Mg1 = -Qy * wa1
Mg1z = Qz * wa1

Mg2 = (-Qy * (wa1 + wa2)) + (Rby * ((wa1 + wa2) - wa1))
Mg2z = (Qz * (wa1 + wa2)) + (Rbz * ((wa1 + wa2) - wa1))

Mg3 = Rdy * wa2
Mg3z = Rdz * wa2

# Obliczenie momentu skręcającego wał szybki [Nmm]
Ms = M0

# Wypadkowe momenty gnące w przekrojach (I - V) [Nmm]
MgI = 0.0
MgII = np.sqrt(Mg1**2 + Mg1z**2)
MgIII = np.sqrt(Mg2**2 + Mg2z**2)
MgIV = np.sqrt(Mg3**2 + Mg3z**2)
MgV = 0.0

# Momenty zredukowane (zastępcze) [Nmm]
Mz2 = np.sqrt((MgII)**2 + ((3 / 16) * (Ms**2)))
Mz3 = np.sqrt((MgIII)**2 + ((3 / 16) * (Ms**2)))
Mz4 = np.sqrt((MgIV)**2 + ((3 / 16) * (Ms**2))) # POPRAWKA: był MgIII zamiast MgIV

# ==============================================================================
# SEKCJA 6: OBLICZENIA WYTRZYMAŁOŚCIOWE WAŁU (ŚREDNICE)
# ==============================================================================
wksj = 0.56 * WRm / Wxz
wkgo = 0.42 * WRm / Wxz
Wk = wkgo  # Dominacja momentu gnącego nad skręcającym

# Minimalne obliczeniowe średnice wału w poszczególnych przekrojach [mm]
Wd1m = np.cbrt((16 * Mz2) / (np.pi * Wk))
Wd2m = np.cbrt((16 * Mz3) / (np.pi * Wk))
Wd3m = np.cbrt((16 * Mz4) / (np.pi * Wk))

# Wpust z tabeli normalizacyjnej
bw = 10   # Szerokość [mm]
hw = 8    # Wysokość [mm]
t1 = 5
t2 = 3.3
zw = 8
wc = 1.6

# Lozyska - obciążenia i nośność
Pd = np.sqrt(Rdy**2 + Rdz**2)
Cd = (Pd / 10) * np.cbrt((Lh * n1) / 16666) # [daN]

# Przyjęte średnice wału [mm] - POPRAWIONO BŁĄD PRZYPISANIA
Wd1 = 30
Wd2 = 34
Wd3 = 28.6
Wd4 = Wd1
Wd5 = Wd4
Wd6 = 35
Wd7 = Wd3
Wd8 = Wd5
Wd9 = Wd8 - 2 * wc
Wd10 = Wd5
Wd11 = Wd6
Wd12 = Wd10
Wd13 = Wd12
Wd14 = Wd7
Wd15 = Wd8
Wd16 = Wd9

# Przyjęte długości odcinków wału [mm]
Wl1 = bz
Wl2 = 5
Wl3 = 1.6
Wl4 = 2.1
Wl5 = 16
Wl6 = wa2 - (Wl3 + Wl4 + (Wl1 + Wl5)/2)
Wl7 = 1.6
Wl8 = 2.1 - wc
Wl9 = wc
Wl10 = Wl5
Wl11 = wa2 - (Wl2 + (Wl10 + Wl1)/2)
Wl12 = bp
Wl13 = wa1 - ((Wl12 + Wl10)/2)
Wl14 = Wl7
Wl15 = Wl8
Wl16 = Wl9

G = 83000 # Moduł Kirchhoffa [MPa]

wszystkie_srednice = [Wd1, Wd2, Wd3, Wd4, Wd5, Wd6, Wd7, Wd8, Wd9, Wd10, Wd11, Wd12, Wd13, Wd14, Wd15, Wd16]
dlugosci_walu = [Wl1, Wl2, Wl3, Wl4, Wl5, Wl6, Wl7, Wl8, Wl9, Wl10, Wl11, Wl12, Wl13, Wl14, Wl15, Wl16]

# ==============================================================================
# SEKCJA 7: SZTYWNOŚĆ SKRĘCNA I ZGINANIA
# ==============================================================================
# Sztywność skrętna
suma_L_di4 = sum(L / (d ** 4) for d, L in zip(wszystkie_srednice, dlugosci_walu) if d > 0)
delta_phi_rad = (32 * Ms / (np.pi * G)) * suma_L_di4
delta_phi_deg = np.rad2deg(delta_phi_rad)
L_total = sum(dlugosci_walu)
phip_rad_mm = delta_phi_rad / L_total
phip_deg_m = phip_rad_mm * 1000 * (180 / np.pi)

d_min = min(wszystkie_srednice)
Jp_min = (np.pi * d_min**4) / 32
phip_max_rad_mm = Ms / (G * Jp_min)
phip_max_deg_m = phip_max_rad_mm * 1000 * (180 / np.pi)

# Obliczenia wpustu
Pp = 2 * M0 / Wd1
wpd = 130
lw = 4 * M0 / (Wd1 * hw * wpd)
Ap = hw/2 * lw
l0 = lw + bw
l0n = 22

# Strzałki ugiecia i kąty ugiecia
suma_di2_li2 = sum(d**2 * l for d, l in zip(wszystkie_srednice, dlugosci_walu))
dz = math.sqrt(suma_di2_li2 / L_total)
Jz = (dz**4) * np.pi / 64
yI = (Qy * wa1 * (wa2**2)) / (4 * E * Jz)
yII = Fr * wa2**3 / (6 * E * Jz)
yIII = yII

phi_BI = 2 * Qy * wa1 * wa2 / (3 * E * Jz)
phi_BII = Fr * wa2**2 / (4 * E * Jz)
phi_DI = -1 * (Qy * wa1 * wa2 / (3 * E * Jz))
phi_DII = -1 * (Qz * wa1 * wa2 / (3 * E * Jz)) # Poprawka: prawdopodobnie Qz zamiast Qy

# ==============================================================================
# SEKCJA 6B: OBLICZENIA WYTRZYMAŁOŚCI NA ZMĘCZENIE WALA
# ==============================================================================
# --- Współczynniki bezpieczeństwa ---
x_1 = 1.3  # [-] współ. kształtu powierzchni
x_2 = 1.4  # [-] współ. wielkości elementu
x_3 = 1.1  # [-] współ. przekształceń
x_4 = 1.1  # [-] współ. warunków pracy
delta_wf = x_1 * x_2 * x_3 * x_4

# --- Granice wytrzymałościowe dla materiału wału (WRm) ---
Zgof = 0.42 * WRm     # [MPa] granica wytrzymałościowa na zginanie
Zsjf = 0.56 * WRm     # [MPa] granica wytrzymałościowa na skręcanie

# --- Wskaźniki wytrzymałościowe z uwzględnieniem osłabienia przez wpust ---
# (Korzysta ze średnicy Wd1 pod wpust oraz wymiarów wpustu bw, t1 z Sekcji 6)
d_f = Wd1
b_f = bw
t_f = t1

Wx_base_f = math.pi * d_f**3 / 32
Wo_base_f = math.pi * d_f**3 / 16
keyway_red_f = (b_f * t_f * (2 * d_f - t_f)**2) / (16 * d_f)

W_xf = Wx_base_f - keyway_red_f  # Wskaźnik na zginanie [mm^3]
W_of = Wo_base_f - keyway_red_f  # Wskaźnik na skręcanie [mm^3]

# --- Naprężenia ---
Mg_max_f = max(MgII, MgIII, MgIV) # Maksymalny moment gnący z poprzednich obliczeń

sigma_af = Mg_max_f / W_xf        # Naprezenie zginajace amplitudowe [MPa]
tau_maxf = Ms / W_of              # Naprezenie skrecajace maksymalne [MPa]
tau_af = tau_maxf / 2             # Naprezenie skrecajace amplitudowe [MPa]

# --- Naprężenia dopuszczalne i weryfikacja ---
sigma_dop_f = Zgof / delta_wf
tau_dop_f = Zsjf / delta_wf

warunek_sigma_f = sigma_af <= sigma_dop_f
warunek_tau_f = tau_af <= tau_dop_f

# ==============================================================================
# SEKCJA F: WYDRUK WYNIKÓW
# ==============================================================================
print("\n" + "=" * 75)
print(" 1. KINEMATYKA UKŁADU I DOBÓR SILNIKA".center(75))
print("=" * 75)
print(f"  Całkowita sprawność układu (η_c)        : {eta_c:<15.4f} [-]")
print(f"  Obliczeniowa moc silnika (N0)           : {N0:<15.3f} [kW]")
print(f"  Teoretyczne przełożenie całkowite (i_c)  : {i_c:<15.3f} [-]")
print(f"  Znormalizowane przełożenie pasowe (i_pn) : {i_pn:<15} [-]")
print(f"  Prędkość obrotowa wału 1 (n1)           : {n1:<15.2f} [obr/min]")
print(f"  Moment skręcający na wałku 1 (M0)       : {M0:<15.2f} [Nmm]")

print("\n" + "=" * 75)
print(" 2. OBLICZENIA PRZEKŁADNI PASOWEJ".center(75))
print("=" * 75)
print(f"  Obliczona odległość osi pasów (A_belt)   : {A_belt:<15.2f} [mm]")
print(f"  Sinus połowy kąta opasania (φ_belt)      : {phi_belt:<15.4f} [rad]")
print(f"  Obliczeniowa liczba pasów (Z_belt)       : {Z_belt:<15.2f} [-]")
print(f"  Przyjęta liczba pasów (Z_up)             : {Z_up:<15} [-]")
print(f"  Szerokość koła pasowego (bp)             : {bp:<15.2f} [mm]")

print("\n" + "=" * 75)
print(" 3. GEOMETRIA I WYTRZYMAŁOŚĆ PRZEKŁADNI ZĘBATEJ".center(75))
print("=" * 75)
print(f"  Wytrzymałość dopuszczalna na zgin. (kg)  : {kg:<15.2f} [MPa]")
print(f"  Kąt przyporu czołowego (α_t)             : {alphat:<15.2f} [°]")
print(f"  Liczba zębów koła 1 (Z1 / Zv1)          : {Z1} / {Zv1:.2f}       [-]")
print(f"  Rzeczywiste przełożenie zębate (i_z)     : {iz:<15.3f} [-]")
print(f"  Liczba zębów koła 2 (Z2 / Zv2)          : {Z2} / {Zv2:.2f}       [-]")
print(f"  Średnice podziałowe (d1 / d2)            : {d1:.2f} / {d2:.2f}   [mm]")
print(f"  Średnice wierzchołkowe (da1 / da2)       : {da1:.2f} / {da2:.2f} [mm]")
print(f"  Średnice stóp zęba (df1 / df2)           : {df1:.2f} / {df2:.2f} [mm]")
print(f"  Prędkość obwodowa (v)                    : {v:<15.2f} [m/s]")
print(f"  Współczynnik dynamiczny (Cd)             : {Cd:<15.4f} [-]")
print(f"  Wskaźniki pokrycia (ε_α / ε_β / ε_γ)    : {ealpha:.3f} / {ebeta:.0f} / {egamma:.3f}")
print(f"  Moduł ze zginania / nacisków (mg/M_nH)   : {mg:.4f} / {M_nH:.4f} [mm]")
print(f"  Ostateczny moduł znormalizowany (mnf)     : {mnf:<15} [mm]")
print(f"  Szerokość wieńca zębatego (bz)           : {bz:<15.2f} [mm]")
print("-" * 75)
print(f"  Siła obwodowa (Ft)                      : {Ft:<15.2f} [N]")
print(f"  Siła promieniowa (Fr)                   : {Fr:<15.2f} [N]")
print(f"  Siła osiowa (Fa)                        : {Fa:<15.2f} [N]")

print("\n" + "=" * 75)
print(" 4. REAKCJE PODPOROWE I MOMENTY GNĄCE".center(75))
print("=" * 75)
print(f"  Odcinki wału (wa1 / wa2 / wa)           : {wa1:.2f} / {wa2:.2f} / {wa:.2f} [mm]")
print("-" * 75)
print(f"  Reakcja Rby                              : {Rby:<15.2f} [N]")
print(f"  Reakcja Rbz                              : {Rbz:<15.2f} [N]")
print(f"  Reakcja Rdy                              : {Rdy:<15.2f} [N]")
print(f"  Reakcja Rdz                              : {Rdz:<15.2f} [N]")
print("-" * 75)
print(f"  Moment skręcający (Ms)                   : {Ms:<15.2f} [Nmm]")
print(f"  Wypadk. mom. gnące (MgII/MgIII/MgIV)    : {MgII:.2f} / {MgIII:.2f} / {MgIV:.2f}")
print(f"  Mom. zredukowane (Mz2 / Mz3 / Mz4)      : {Mz2:.2f} / {Mz3:.2f} / {Mz4:.2f}")

print("\n" + "=" * 75)
print(" 5. PROJEKTOWANIE WYMIARÓW WAŁU".center(75))
print("=" * 75)
print(f"  Dopuszczalne naprężenie (Wk)             : {Wk:<15.2f} [MPa]")
print(f"  Min. średnice (Wd1m / Wd2m / Wd3m)      : {Wd1m:.2f} / {Wd2m:.2f} / {Wd3m:.2f} [mm]")
print("-" * 75)
print("  Odcinek    Średnica Ø [mm]    Długość [mm]")
print("-" * 75)
for i, (d, l) in enumerate(zip(wszystkie_srednice, dlugosci_walu), 1):
    print(f"     {i:2d}          {d:5.0f}             {l:6.2f}")
print("-" * 75)
print(f"  CAŁKOWITA DŁUGOŚĆ WAŁU                   : {L_total:<15.2f} [mm]")

print("\n" + "=" * 75)
print(" 6. WERYFIKACJA SZTYWNOŚCI WAŁU".center(75))
print("=" * 75)

print("\n  >> Sztywność skrętna:")
print("  " + "-" * 50)
print(f"  Całkowity kąt skręcenia (Δφ)             : {delta_phi_deg:<15.4f} [°]")
print(f"  Średni kąt skręcenia (φ')                : {phip_deg_m:<15.4f} [°/m]")
print(f"  Maks. lokalny kąt skręcenia (φ'_max)     : {phip_max_deg_m:<15.4f} [°/m]")

print("\n  >> Sztywność na zginanie (ugięcia):")
print("  " + "-" * 50)
print(f"  Strzałka ugięcia yI                      : {yI:<15.6f} [mm]")
print(f"  Strzałka ugięcia yII                     : {yII:<15.6f} [mm]")
print(f"  Suma strzałek ugieć (yI+yII+yIII)        : {yI+yII+yIII:<15.6f} [mm]")
print(f"  Warunek ugięcia (<= 0.005*mnf)           : {0.005*mnf:<15.6f} [mm]")
y_check = "SPENIONY" if (yI+yII+yIII) <= (0.005*mnf) else "NIESPENIONY!"
print(f"  Status warunku ugięcia                   : >>> {y_check} <<<")

print("\n  >> Sztywność na zginanie (kąty ugiecia podpór):")
print("  " + "-" * 50)
print(f"  Kąt ugiecia podpora B (φ_BI + φ_BII)     : {abs(phi_BI) + abs(phi_BII):<15.6f} [rad]")
print(f"  Kąt ugiecia podpora D (φ_DI + φ_DII)     : {abs(phi_DI) + abs(phi_DII):<15.6f} [rad]")
print(f"  Warunek kątów (<= 0.0023 rad)            : {0.0023:<15.6f} [rad]")
phi_check = "SPENIONY" if (abs(phi_BI) + abs(phi_BII) <= 0.0023 and abs(phi_DI) + abs(phi_DII) <= 0.0023) else "NIESPENIONY!"
print(f"  Status warunku kątów ugiecia             : >>> {phi_check} <<<")

print("\n" + "=" * 75)
print(" 7. DOBÓR ŁOŻYSKA I WPUSTU".center(75))
print("=" * 75)
print(f"  Siła zastępcza na łożysko D (Pd)         : {Pd:<15.2f} [N]")
print(f"  Wymagana nośność dynamiczna (Cd)         : {Cd:<15.2f} [daN]")
print(f"  Sugerowane łożysko                       : 6204")
print("-" * 75)
print(f"  Długość obliczeniowa wpustu (lw)         : {lw:<15.2f} [mm]")
print(f"  Długość nominalna wpustu (l0n)           : {l0n:<15} [mm]")
print("=" * 75 + "\n")
print("\n" + "=" * 75)
print(" 6B. WYTRZYMAŁOŚĆ NA ZMĘCZENIE WALA".center(75))
print("=" * 75)
print(f"  Współczynnik wytrzymałościowy (δ_w)        : {delta_wf:<15.2f} [-]")
print(f"  Wytrzymałość na zginanie (Z_go)            : {Zgof:<15.0f} [MPa]")
print(f"  Wytrzymałość na skręcanie (Z_sj)           : {Zsjf:<15.0f} [MPa]")
print("-" * 75)
print(f"  Średnica wału w przekroju (d)              : {d_f:<15.0f} [mm]")
print(f"  Wskaźnik na zginanie (W_x)                : {W_xf:<15.3f} [mm³]")
print(f"  Wskaźnik na skręcanie (W_o)                : {W_of:<15.3f} [mm³]")
print("-" * 75)
print(f"  Maks. moment gnący (Mg_max)                : {Mg_max_f:<15.2f} [Nmm]")
print(f"  Naprężenie zginające σ_a                   : {sigma_af:<15.3f} [MPa]")
print(f"  Naprężenie skr. amplitudowe τ_a            : {tau_af:<15.3f} [MPa]")
print("-" * 75)
print(f"  Dopuszczalne napr. zginające               : {sigma_dop_f:<15.2f} [MPa]")
print(f"  Dopuszczalne napr. skr. amplitudowe        : {tau_dop_f:<15.2f} [MPa]")
print("  " + "-" * 71)
print(f"  Warunek σ_a <= dopuszcz.                   : {'SPENIONY' if warunek_sigma_f else 'NIESPENIONY!'}")
print(f"  Warunek τ_a <= dopuszcz.                   : {'SPENIONY' if warunek_tau_f else 'NIESPENIONY!'}")
print("=" * 75)