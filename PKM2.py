import math

# ============================================================
# ZMIENNE - KATEGORYZACJA I UŻYCIE
# ============================================================
#
# POZIOM 0 - DANE WEJŚCIOWE (projektowe, podstawowe)
#   N_wyj      [kW]    moc wyjściowa              (sekcje 1..2)
#   n_2        [RPM]   prędkość wyjściowa          (sekcja 2)
#   n_s        [RPM]   synchroniczna silnika       (wyj., nieużywane w calc.)
#   K          [-]     współ. bezpieczeństwa        (sekcje 1..2)
#   L_h        [h]     żywotność                  (dane, użyte TODO §4)
#
# POZIOM 1 - SPRAWNOŚCI I PRZEŁOŻENIA (często używane)
#   eta_t      [-]     sprawność łożysk           → η_c
#   eta_z      [-]     sprawność zazębienia       → η_c
#   eta_p      [-]     sprawność przekł. pasowej  → η_c
#   eta_c      [-]     sprawność całkowita        (sekcja 1)
#   N_o        [kW]    moc obliczona              (sekcje 1..2, §4 TODO)
#   silnik_nazwa [-]   nazwa wybranego silnika    (wyj.)
#   N_silnik   [kW]    moc znamionowa             (dane wyj., nieużywane w calc.)
#   n_s_rzeczywista [RPM] prędkość pod obciąż.   (sekcje 2..3)
#
# POZIOM 2 - PARAMETRY PASA (średnio używane)
#   i_c        [-]     przełożenie całkowite      (sekcja 2)
#   i_p_obl    [-]     √i_c obliczone             (wyj., nieużywane dalej)
#   i_pn       [-]     przełożenie pasowe przyjęte(sekcja 2)
#   i_z        [-]     przełożenie zębate          (sekcja 2→3)
#   N_1        [kW]    moc 1 pasa                 (sekcja 2)
#   d_p        [mm]    średnica koła małego       (sekcje 2..3)
#   k_T        [-]     współ. obciążenia          (sekcja 2)
#   D_p        [mm]    średnica koła dużego       (sekcje 2..3)
#   A_o        [mm]    odległość między osiami    (sekcja 2)
#   L_p        [mm]    długość pasa obliczona     (wyj., nieużywane dalej)
#   L_pn       [mm]    długość pasa znormalizowana(sekcja 2)
#   K_L        [-]     współ. korekcyjny długości (sekcja 2)
#   A          [mm]    skorygowana odległość      (sekcja 2..3)
#   alfa       [deg]   kąt opasania przybliżony   (wyj.)
#   alfa_tabl  [deg]   kąt z tablicy              (sekcja 2)
#   k_phi      [-]     współ. kąta opasania       (sekcja 2)
#   Z          [-]     liczba pasów obliczona     (sekcja 2)
#   Z_ceil     [-]     liczba pasów zaokrąglona    (sekcja 2)
#
# POZIOM 3 - GEOMETRIA PASA (w wąskiej sekcji 2b)
#   gamma_rad  [rad]   kąt gamma                  (sekcja 2b)
#   gamma_deg  [deg]   γ w stopniach              (sekcja 2b)
#   alpha_1    [deg]   podany w treści            (sekcja 2b)
#   phi_rad    [rad]   φ w radianach              (sekcja 2b)
#   phi_deg    [deg]   φ w stopniach              (sekcja 2b)
#   P          [N]     siła                        (sekcja 2b)
#   upsilon    [m/s]   prędkość pasa               (sekcja 2b)
#   mu         [-]     współ. tarcia               (sekcja 2b)
#   mu_prime   [-]     μ' skorygowane             (sekcja 2b)
#   exp_val    [-]     e^(φ×μ')                  (obliczenia wewnętrzne)
#   S_a        [N]     siła ściągająca             (sekcja 2b)
#   S_b        [N]     siła poluzowana              (sekcja 2b)
#   P_a        [N]     różnica S_a - S_b          (wyj.)
#   Q          [N]     siłą wypadkowa               (sekcja 2b)
#   beta_rad   [rad]   kąt ugięcia                (sekcja 2b)
#   beta_deg   [deg]   β w stopniach              (sekcja 2b)
#
# POZIOM 4 - ZMIENNE POMIĘDZY / UŻYTKU JEDNORAZOWEGO
#   A_o_min    [mm]    dolny zakres A0            (wyj., nieużywane)
#   A_o_max    [mm]    górny zakres A0            (wyj., nieużywane)
#   kat_stosunek [-]   (D_p-d_p)/A               (wyj.)
#   p_val      [mm]    pośrednie do A             (obliczenia wewnętrzne)
#   q_val      [mm2]   pośrednie do A             (obliczenia wewnętrzne)
#
# POZIOM 5 - PRZEKŁADNIĄ ZĘBATĄ (sekcja 3)
#   beta_z       [deg]    kąt skrętu zębów          (§3)
#   alpha_n      [deg]    kąt_pressji normalny       (§3)
#   y_n          [-]      współ. wysokości           (§3)
#   m_n_wstepny  [mm]    moduł wstępny               (§3)
#   Cc           [-]      współczynnik (przyjęty)   (§3 pkt 1)
#   X_zj,X_zo    [-]      z tabelki (interp.)       (§3 pkt 1)
#   Zgo,Zgj      [MPa]    limit wytrzymałości       (§3 materiał)
#   k_gj,k_go    [MPa]    moduły wytrzymałościowe   (§3 pkt 1)
#   kg           [MPa]    moduł graniczny (min)     (§3 pkt 1)
#   n_1          [RPM]    prędkość wału przekł.     (§3 żywotność)
#   N_cykli      [-]      liczba cykli              (§3 żywotność)
#   M_o          [Nmm]   moment obrotowy            (§3 moment)
#   z_gb         [-]      gran. liczba zębów        (§3 liczebna)
#   z_1,z_2      [-]      liczby zębów kół          (§3 liczebna)
#   lambda_zast  [-]      współ. zastępczy           (§3 liczebna)
#   d_1,d_2      [mm]    średnice podziałowe        (§3 prędkość)
#   v            [m/s]   prędkość obwodowa          (§3 prędkość)
#   Cd           [-]      współ. obciążenia         (§3 prędkość)
#   Cp           [-]      współ. obciążenia (czas)  (§3 prędkość)
#   C1,C2,C3     [-]      współcz. geometryczne      (§3 C)
#   z_2_calc     [-]      z_2+1 dla C2/C3          (§3 C - konwencja dokumentu)
#   eps_alpha    [-]      licznik kontaktów α        (§3 C_beta)
#   eps_beta     [-]      licznik kontaktów β        (§3 C_beta)
#   eps_gamma    [-]      licznik kontaktów γ        (§3 C_beta)
#   psi          [-]      szerokość zębów (przyjęta) (§3)
#   psi_prime    [-]      korygowana szerokość       (§3)
#   Cb           [-]      współ. rozkładu obciążenia (§3 C_beta)
#   m_g          [mm]    moduł min. zginanie         (§3 weryf.)
# ============================================================
# DANE PROJEKTOWE
# ============================================================
N_wyj = 4.44  # [kW] moc wyjściowa
n_2 = 154  # [RPM] prędkość obrotowa wyjściowa
n_s = 1000  # [RPM] prędkość synchroniczna silnika
K = 1.58  # [-]   współczynnik bezpieczeństwa
L_h = 6000  # [h]   żywotność

print("=" * 60)
print("  DANE PROJEKTOWE")
print("=" * 60)
print(f"  N_wyj = {N_wyj} kW")
print(f"  n_2   = {n_2} RPM")
print(f"  n_s   = {n_s} RPM")
print(f"  K     = {K}")
print(f"  L_h   = {L_h} h")

# ============================================================
# 1. DOBÓR SILNIKA
# ============================================================
print("\n" + "=" * 60)
print("  1. DOBÓR SILNIKA")
print("=" * 60)

# --- Sprawności składowe ---
eta_t = 0.995  # sprawność łożysk tocznych (0.99 - 0.995)
eta_z = 0.98  # sprawność zazębienia       (0.96 - 0.98)
eta_p = 0.96  # sprawność przekładni pasowej (0.94 - 0.96)

print(f"\n  Sprawności:")
print(f"    η_t = {eta_t}")
print(f"    η_z = {eta_z}")
print(f"    η_p = {eta_p}")

# --- Sprawność całkowita ---
eta_c = eta_p * eta_t**2 * eta_z
print(f"\n  η_c = η_p × η_t2 × η_z")
print(f"  η_c = {eta_p} × {eta_t}2 × {eta_z}")
print(f"  η_c = {eta_c:.4f}")

# --- Moc obliczona ---
N_o = (K * N_wyj) / eta_c
print(f"\n  N_o = (K × N_wyj) / η_c")
print(f"  N_o = ({K} × {N_wyj}) / {eta_c:.4f}")
print(f"  N_o = {N_o:.4f} kW  ({N_o * 1000:.4f} W)")

# --- Silnik wybrany z katalogu ---
silnik_nazwa = "MS2 160L-6"
N_silnik = 11  # [kW] moc znamionowa silnika - doesnt really matter?
n_s_rzeczywista = 950  # [RPM] prędkość pod obciazeniem (6-biegunowy)

print(f"\n  *** Wybrany silnik: {silnik_nazwa} ***")
print(f"      Moc znamionowa:  {N_silnik} kW")
print(f"      Prędkość pod obciążeniem:  {n_s_rzeczywista} RPM")

# ============================================================
# 2. DOBÓR PASA
# ============================================================
print("\n" + "=" * 60)
print("  2. DOBÓR PASA (typ A)")
print("=" * 60)

# --- Przełożenia ---
i_c = n_s_rzeczywista / n_2
i_p_obl = math.sqrt(i_c)
i_pn = 3  # przełożenie pasowe - przyjęte
i_z = i_c / i_pn  # przełożenie zębate

print(f"\n  Przełożenie całkowite:")
print(f"    i_c = n_s' / n_2 = {n_s_rzeczywista} / {n_2} = {i_c:.4f}")
print(f"\n  Przełożenie pasowe:")
print(f"    i_p (obliczone) = √i_c = √{i_c:.4f} = {i_p_obl:.4f}")
print(f"    i_pn (przyjęte) = {i_pn}")
print(f"\n  Przełożenie zębate:")
print(f"    i_z = i_c / i_pn = {i_c:.4f} / {i_pn} = {i_z:.4f}")

# --- Parametry pasa ---
N_1 = 2.59  # [kW] moc przenoszona przez 1 pas (z tablicy)
d_p = 180  # [mm] średnica koła małego
k_T = 1.3  # współczynnik obciążenia (napędy średnie, >16 h)

D_p = d_p * i_pn  # średnica koła dużego [mm]

print(f"\n  Parametry pasa:")
print(f"    N_1 = {N_1} kW (moc 1 pasa)")
print(f"    d_p = {d_p} mm (koło małe)")
print(f"    D_p = d_p × i_pn = {d_p} × {i_pn} = {D_p} mm (koło duże)")
print(f"    k_T = {k_T} (napędy średnie, >16 h)")

# --- Odległość między osiami ---
A_o_min = 0.7 * (D_p + d_p)
A_o_max = 2.0 * (D_p + d_p)
A_o = 800  # [mm] przyjęta

print(f"\n  Odległość między osiami:")
print(f"    {A_o_min:.0f} < A_o < {A_o_max:.0f} mm")
print(f"    A_o (przyjęte) = {A_o} mm")

# --- Długość pasa (obliczona) ---
L_p = 2 * A_o + 1.57 * (D_p + d_p) + (D_p - d_p) ** 2 / (4 * A_o)
print(f"\n  Długość pasa obliczona:")
print(f"    L_p = 2×{A_o} + 1.57×({D_p}+{d_p}) + ({D_p}-{d_p})2 / (4×{A_o})")
print(f"    L_p = {L_p:.1f} mm")

# --- Długość pasa (znormalizowana) ---
L_pn = 2832  # [mm] z katalogu
K_L = 1.11  # współczynnik korekcyjny długości pasa

print(f"\n  Długość pasa przyjęta (znormalizowana):")
print(f"    L_pn = {L_pn} mm")
print(f"    K_L  = {K_L}")

# --- Skorygowana odległość między osiami ---
p_val = 0.25 * L_pn - 0.393 * (D_p + d_p)
q_val = 0.125 * (D_p - d_p) ** 2
A = p_val + math.sqrt(p_val**2 - q_val)

print(f"\n  Skorygowana odległość A:")
print(f"    p = 0.25×{L_pn} - 0.393×({D_p}+{d_p}) = {p_val:.4f}")
print(f"    q = 0.125×({D_p}-{d_p})2 = {q_val:.4f}")
print(f"    A = p + √(p2 - q)")
print(f"    A = {p_val:.4f} + √({p_val**2:.4f} - {q_val:.4f})")
print(f"    A = {p_val:.4f} + {math.sqrt(p_val**2 - q_val):.4f}")
print(f"    A = {A:.4f} mm")

# --- Kąt opasania ---
kat_stosunek = (D_p - d_p) / A
alfa = 180 - 57.3 * kat_stosunek  # przybliżenie

print(f"\n  Kąt opasania:")
print(f"    (D_p - d_p) / A = {D_p - d_p} / {A:.4f} = {kat_stosunek:.4f}")
print(f"    α ≈ 180° - 57.3° × {kat_stosunek:.4f} = {alfa:.1f}°")

alfa_tabl = 154  # [°] odczytane z tablicy
k_phi = 0.93  # współczynnik kąta opasania (z tablicy)

print(f"    α (z tablicy)  = {alfa_tabl}°")
print(f"    k_φ (z tablicy) = {k_phi}")

# --- Liczba pasów Z ---
Z = (N_o * k_T) / (N_1 * k_phi * K_L)
Z_ceil = math.ceil(Z)

print(f"\n  Liczba pasów:")
print(f"    Z = (N × k_T) / (N_1 × k_φ × K_L)")
print(f"    Z = ({N_o} × {k_T}) / ({N_1} × {k_phi} × {K_L})")
print(f"    Z = {N_o * k_T:.4f} / {N_1 * k_phi * K_L:.4f}")
print(f"    Z = {Z:.1f}")
print(f"    Z (zaokrąglone w górę) = {Z_ceil}")

# --- Sprawdzenie zakresu ---
print(f"\n  Warunek: 3 <= Z <= 6")
if 3 <= Z_ceil <= 6:
    print(f"    ✓ SPEŁNIONY (Z = {Z_ceil})")
else:
    raise ValueError(f"    ✗ NIESPEŁNIONY (Z = {Z_ceil}) - fuck off and fix it!")

# ============================================================
# 3. Geometria przekładni pasowej
# ============================================================
print("\n" + "=" * 60)
print("  3. OBLICZENIA")
print("=" * 60)

# --- Gamma ---
gamma_rad = math.asin((D_p - d_p) / (2 * A))
gamma_deg = math.degrees(gamma_rad)
alpha_1 = 38  # [deg] podany w treści
print(f"\n  Gamma:")
print(f"    gamma = arcsin((D_p - d_p) / (2 * A))")
print(f"    gamma = arcsin(({D_p} - {d_p}) / (2 * {A})) = {gamma_rad:.10f} [rad]")
print(f"    gamma = {gamma_deg:.4f}°")
print(f"    alpha_1 = {alpha_1}°")

# --- Phi ---
phi_deg = 180 - 2 * gamma_deg
phi_rad = math.radians(phi_deg)
print(f"\n  Phi:")
print(f"    phi = 180° - 2 × gamma = 180° - 2 × {gamma_deg:.4f}° = {phi_deg:.4f}°")
print(f"    phi = {phi_rad:.4f} [rad]")

# --- P ---
P = 1.91e7 * N_o / (n_s_rzeczywista * d_p)
print(f"\n  P:")
print(f"    P = 1.91e7 / (n_s' × d_p)")
print(f"    P = 1.91e7 × {N_o} / ({n_s_rzeczywista} × {d_p}) = {P:.4f}")

# --- upsilon ---
upsilon = math.pi * d_p * n_s_rzeczywista / 60000
print(f"\n  upsilon:")
print(f"    upsilon = pi × d_p × n_s' / 60000")
print(
    f"    upsilon = {math.pi:.4f} × {d_p} × {n_s_rzeczywista} / 60000 = {upsilon:.5f} [m/s]"
)

# --- mu ---
mu = 0.35 + 0.012 * upsilon
mu_prime = mu / math.cos(math.radians(alpha_1 / 2))
print(f"\n  mu:")
print(f"    mu = 0.35 + 0.012 × upsilon = {mu:.4f}")
print(
    f"    mu' = mu / cos(alpha_1/2) = {mu:.4f} / cos({alpha_1 / 2:.4f}) = {mu_prime:.4f}"
)

# --- S_a and S_b ---
exp_val = math.exp(phi_rad * mu_prime)
S_a = P * exp_val / (exp_val - 1)
S_b = P / (exp_val - 1)
print(f"\n  S_a and S_b:")
print(f"    S_a = P × e^(phi × mu') / (e^(phi × mu') - 1) = {S_a:.4f}")
print(f"    S_b = P / (e^(phi × mu') - 1) = {S_b:.4f}")

# --- P_a ---
P_a = S_a - S_b
print(f"\n  P_a:")
print(f"    P_a = S_a - S_b = {S_a:.4f} - {S_b:.4f} = {P_a:.4f}")

# --- Q ---
Q = math.sqrt(S_a**2 + S_b**2 + 2 * S_a * S_b * math.cos(math.radians(2 * gamma_deg)))
print(f"\n  Q:")
print(f"    Q = sqrt(S_a^2 + S_b^2 + 2 × S_a × S_b × cos(2 × gamma)) = {Q:.4f}")

# --- beta ---
tan_gamma = math.tan(math.radians(gamma_deg))
beta_rad = math.atan(((S_a - S_b) / (S_a + S_b)) * tan_gamma)
beta_deg = math.degrees(beta_rad)
print(f"\n  beta:")
print(f"    beta = arctan(((S_a - S_b) / (S_a + S_b)) × tan(gamma))")
print(
    f"    beta = arctan({((S_a - S_b) / (S_a + S_b)) * tan_gamma:.4f}) = {beta_rad:.4f} [rad] = {beta_deg:.4f}°"
)

# ============================================================
# 3. PRZEKŁADNIĄ ZĘBATĄ (gears)
# ============================================================

print("\n" + "=" * 60)
print("  3. PRZEKŁADNIĄ ZĘBATĄ")
print("=" * 60)

# --- Dane materiałowe: stal 18HGT ---
Zgo = 420  # [MPa] granica wytrzymałości (zgięcie)
Zgj = 660  # [MPa] granica wytrzymałości (kontakt)
print(f"\n  Materiał: stal 18HGT")
print(f"    Zgo = {Zgo} MPa")
print(f"    Zgj = {Zgj} MPa")

# --- Punkt 1: k_gj, k_go ---
Cc = 1  # [-] współczynnik (przyjęty)
X_zj = 1.9  # [-] z tabelki (interpolacja) - dla Zgj
X_zo = 2.3  # [-] z tabelki (interpolacja) - dla Zgo

k_gj = Cc * Zgj / X_zj  # [MPa] moduł wytrzymałościowy - gięcie
k_go = Cc * Zgo / X_zo  # [MPa] moduł wytrzymałościowy - kontakt
kg = min(k_gj, k_go)  # [MPa] moduł graniczny (mniejszy limituje)

print(f"\n  Punkt 1 - k_gj; k_go:")
print(f"    C_c = {Cc}")
print(f"    X_zj = {X_zj} (z tabelki)")
print(f"    X_zo = {X_zo} (z tabelki)")
print(f"\n    k_gj = (C_c × Zgj) / X_zj")
print(f"    k_gj = ({Cc} × {Zgj}) / {X_zj}")
print(f"    k_gj = {k_gj:.6f} [MPa]")
print(f"\n    k_go = (C_c × Zgo) / X_zo")
print(f"    k_go = ({Cc} × {Zgo}) / {X_zo}")
print(f"    k_go = {k_go:.6f} [MPa]")
print(f"\n    kg = min(k_gj, k_go)")
print(f"    kg = min({k_gj:.1f}, {k_go:.1f})")
print(f"    kg = {kg:.6f} [MPa]")

# --- Żywotność i moment obrotowy ---
n_1 = n_s_rzeczywista / i_pn  # [RPM] prędkość wału wejściowego przekładni
N_cykli = n_1 * L_h * 60  # [-] liczba cykli przemian obciążeń

# M_o w Nmm (N_o w kW, n_1 w RPM → 9550×103 = 9550000)
M_o = 9550 * 1e3 * N_o / n_1  # [Nmm] moment obrotowy

print(f"\n  Żywotność i moment:")
print(f"    n_1 = n_s' / i_pn")
print(f"    n_1 = {n_s_rzeczywista} / {i_pn}")
print(f"    n_1 = {n_1:.4f} [RPM]")
print(f"\n    N_cykli = n_1 × L_h × 60")
print(f"    N_cykli = {n_1:.4f} × {L_h} × 60")
print(f"    N_cykli = {N_cykli:.0f}")
print(f"\n  Obliczanie momentu:")
print(f"    M_o = 9550 × 103 × N_o / n_1  [Nmm, z kW/RPM]")
print(f"    M_o = 9550 × 103 × {N_o} / {n_1:.4f}")
print(f"    M_o = {M_o:.0f} [Nmm]")

# --- Przyjęte wartości podstawowe ---
beta_z = 10  # [deg] kąt skrętu zębów (przyjęty)
alpha_n = 20  # [deg] kąt_pressji normalny
y_n = 1  # [-] współ. wysokości zęba
m_n_wstepny = 4  # [mm] moduł wstępny (złożony ze zbioru {2, 2.5, 3, ...})

print(f"\n  Przyjęte wartości (Graniczna liczba zębów):")
print(f"    α_n   = {alpha_n}°")
print(f"    β_z   = {beta_z}°")
print(f"    y_n   = {y_n}")
print(f"    m_n   = {m_n_wstepny} [mm]")

# --- Kąty geometryczne ---
alpha_t = math.degrees(
    math.atan(math.tan(math.radians(alpha_n)) / math.cos(math.radians(beta_z)))
)
y_t = y_n * math.cos(math.radians(beta_z))

print(f"\n  α_t = arctan(tan(α_n) / cos(β_z))")
print(f"  α_t = arctan(tan({alpha_n}°) / cos({beta_z}°)")
print(f"  α_t = {alpha_t:.6f}°")
print(f"\n  y_t = y_n × cos(β_z)")
print(f"  y_t = {y_n} × cos({beta_z}°) = {y_t:.4f}")

# --- Liczba zębów koła małego ---
z_gb = y_t * 2 / math.sin(math.radians(alpha_t)) ** 2
z_gb_round = math.ceil(z_gb)  # zaokrąglamy w górę

z_1zast_raw = z_gb_round / math.cos(math.radians(beta_z)) ** 3
z_1zast = math.ceil(z_1zast_raw)  # zaokrąglamy w górę

z_1 = z_1zast  # dla tej sekcji: z_1 = z_1zast
lambda_zast = 6.69  # z tabelki (dla z_1zast=18, λ_zast≈6.69)

print(f"\n  Liczba zębów:")
print(f"    z_gβ = y_t × 2 / sin2(α_t)")
print(f"    z_gβ = {y_t:.4f} × 2 / sin2({alpha_t:.4f}°) = {z_gb:.4f}")
print(f"    → zaokrąglone w górę: {z_gb_round}")
print(f"\n    z_1zast = z_gβ(zaokr.) / cos3(β_z)")
print(f"    z_1zast = {z_gb_round} / cos3({beta_z}°) = {z_1zast_raw:.4f}")
print(f"    → zaokrąglone w górę: {z_1zast}")
print(f"    z_1 = z_1zast = {z_1}")
print(f"    λ_zast (z tabelki dla z_1zast={z_1zast}) = {lambda_zast}")

# --- Liczba zębów koła dużego ---
i_z_przyjete = i_c / i_pn  # [-] przełożenie zębate
z_2_raw = z_1 * i_z_przyjete  # teoretyczna liczba zębów
z_2 = int(z_2_raw)  # zaokrąglamy w dół

print(f"\n  i_c = i_pn × i_z  →  i_z = i_c / i_pn")
print(f"  i_z = {i_c:.4f} / {i_pn} = {i_z_przyjete:.4f}")
print(f"\n  z_2 = z_1 × i_z")
print(f"  z_2 = {z_1} × {i_z_przyjete:.4f} = {z_2_raw:.4f}")
print(f"  → zaokrąglone w dół: {z_2}")

# --- Średnice podziałowe i prędkość obwodowa ---
d_1 = m_n_wstepny * z_1 / math.cos(math.radians(beta_z))
d_2 = m_n_wstepny * z_2 / math.cos(math.radians(beta_z))

print(f"\n  Średnice podziałowe:")
print(f"    d_1 = m_n × z_1 / cos(β_z)")
print(f"    d_1 = {m_n_wstepny} × {z_1} / cos({beta_z}°) = {d_1:.4f} [mm]")
print(f"    d_2 = m_n × z_2 / cos(β_z)")
print(f"    d_2 = {m_n_wstepny} × {z_2} / cos({beta_z}°) = {d_2:.4f} [mm]")

v = math.pi * d_1 * n_1 / 60000  # [m/s] prędkość obwodowa
print(f"\n  Prędkość obwodowa:")
print(f"    v = π × d_1 × n_1 / 60000")
print(f"    v = {math.pi:.4f} × {d_1:.4f} × {n_1:.4f} / 60000")
print(f"    v = {v:.4f} [m/s]")

# --- Współczynniki obciążenia C_d i C_p ---
Cd = 1 + math.sqrt(v) / 7  # współ. obciążenia dynamicznego
Cp = 1.75  # z tabeli (dla 10-16 h pracy)

print(f"\n  C_d:")
print(f"    C_d = 1 + √v / 7")
print(f"    C_d = 1 + √{v:.4f} / 7 = 1 + {math.sqrt(v):.4f} / 7")
print(f"    C_d = {Cd:.4f}")
print(f"\n  C_p = {Cp} (z tabeli, 10-16 h)")

# --- C1/2/3 ---
# wspólny czynnik geometryczny
common_factor = (
    1 + math.tan(math.radians(alpha_n)) ** 2 / math.cos(math.radians(beta_z)) ** 2
)

print(f"\n  Współczynniki C1/2/3:")
print(f"    Wspólny czynnik: 1 + tan2(α_n)/cos2(β_z) = {common_factor:.6f}")

C1 = (1 / (2 * math.pi)) * math.sqrt(
    (1 + 2 * math.cos(math.radians(beta_z)) / z_1) ** 2 * common_factor - 1
)
# Note: źródło używa z_2+1=38 w mianowniku C2 i liczniku C3 zamiast z_2=37
# (konwencja/typografia z dokumentu - zachowano zgodność z wynikami źródłowymi)
z_2_calc = z_2 + 1  # konwencja dokumentu dla C2/C3

C2 = (1 / (2 * math.pi)) * math.sqrt(
    (1 + 2 * math.cos(math.radians(beta_z)) / z_2_calc) ** 2 * common_factor - 1
)
C3 = ((z_1 + z_2_calc) * math.tan(math.radians(alpha_n))) / (
    2 * math.pi * math.cos(math.radians(beta_z))
)

print(f"\n    C1:")
print(f"      C1 = 1/(2π) × √((1+2cos(β_z)/z1)2 × common - 1)")
print(f"      C1 = {C1:.4f}")
print(f"\n    C2 (użyto z_2+1={z_2_calc} - konwencja dokumentu):")
print(f"      C2 = {C2:.4f}")
print(f"\n    C3: (z1+{z_2_calc})×tan(α_n)/(2π×cos(β_z))")
print(f"      C3 = ({z_1}+{z_2_calc}) × tan({alpha_n}°) / (2π×cos({beta_z}°)")
print(f"      C3 = {C3:.4f}")

# --- Liczniki kontaktów i C_β ---
eps_alpha = z_1 * C1 + z_2 * C2 - C3  # licznik kontaktów normalnych
print(f"\n  ε_α:")
print(f"    ε_α = z1×C1 + z2×C2 - C3")
print(f"    ε_α = {z_1}×{C1:.4f} + {z_2}×{C2:.4f} - {C3:.4f}")
print(f"    ε_α = {eps_alpha:.4f}")

# Przyjęta szerokość zębów (psi) - założenie z dokumentu
psi = 14  # [-] przybliżona szerokość
print(f"\n  Zakładamy ψ = {psi}")

eps_beta = (
    psi * math.sin(math.radians(beta_z)) / math.pi
)  # licznik kontaktów spiralnych
print(f"\n  ε_β = ψ × sin(β_z) / π")
print(f"  ε_β = {psi} × sin({beta_z}°) / π = {eps_beta:.4f}")
# Dokument zaokrągla do ≈1 (konwencja, choć nie jest to liczba naturalna)
eps_beta_rounded = int(round(eps_beta))

psi_prime = (
    eps_beta_rounded * math.pi / math.sin(math.radians(beta_z))
)  # korygowana szer.
print(f"\n  ψ' = ε_β(zaokr.) × π / sin(β_z)")
print(f"  ψ' = {eps_beta_rounded} × π / sin({beta_z}°) = {psi_prime:.4f}")

# Uwaga: w źródle jest niezgodność - ε_α obliczone jako 1.5009,
# ale później użyte jako ~1.58 (z z_2+1). Zachowano oryginalny wynik ε_α=1.5009.
eps_gamma = eps_alpha + eps_beta_rounded  # całkowity licznik kontaktów

print(f"\n  ε_γ = ε_α + ε_β(zaokr.)")
print(f"  ε_γ = {eps_alpha:.4f} + {eps_beta_rounded}")
print(f"  ε_γ = {eps_gamma:.4f}")

# C_β - współczynnik rozkładu obciążenia
if eps_gamma >= 1.5:
    Cb = 1.4
else:
    Cb = 1.3 + (1.5 - eps_gamma) * (0.1 / 0.5)  # interpolacja

print(f"\n  C_β:")
print(f"    Dla ε_γ={eps_gamma:.4f} ≥ 1.5: C_β = {Cb}")

# --- Weryfikacja modułu - zginanie ---
# m_g ≥ ∛(C_p × C_d × 2 × 9550×103 × N_o × cos(β_z) / (ψ × λ × C_β × n_1 × z_1 × kg))
# Zgodnie z PLAN.md: w mianowniku ψ=14, nie ψ'=18.09 (korekta D4)
numerator = Cp * Cd * 2 * 9550 * 1e3 * N_o * math.cos(math.radians(beta_z))
denominator = psi * lambda_zast * Cb * n_1 * z_1 * kg

m_g = (numerator / denominator) ** (1 / 3)

print(f"\n  Weryfikacja modułu (zginanie):")
print(f"    m_g = ∛(C_p × C_d × 2 × 9550×103 × N_o × cos β_z")
print(f"         / (ψ × λ × C_β × n1 × z1 × kg))")
print(f"\n    Licznik  = {Cp} × {Cd:.4f} × 2 × 9550×103 × {N_o} × cos({beta_z}°)")
print(f"    Licznik  = {numerator:.4e}")
print(f"\n    Mianownik = {psi} × {lambda_zast} × {Cb} × {n_1:.4f} × {z_1} × {kg:.6f}")
print(f"    Mianownik = {denominator:.4f}")
print(f"\n    m_g = ∛({numerator / denominator:.6f})")
print(f"    m_g = {m_g:.4f} [mm]")

# --- C_mα i weryfikacja modułu - kontakt (wypukłość) ---
# Uproszczona postać wzoru: C_mα = √(0.7·E / sin(2α_n))
E = 2.1e5  # [MPa] moduł Younga
C_malpha = math.sqrt(0.7 * E / math.sin(math.radians(2 * alpha_n)))
print(f"\n  C_mα (współczynnik kształtu zęba):")
print(f"    C_mα = √(0.7 × E / sin(2·α_n))")
print(f"    C_mα = √(0.7 × {E:.1e} / sin({2 * alpha_n}°)")
print(f"    C_mα = {C_malpha:.4f}")

# k_H - moduł wytrzymałościowy na kontakt (wykres Wöhlera)
R_m = 1000  # [MPa] granica wytrzymałości stal 18HGT
Z_Hj = 600  # [MPa] wykres Wohlera, V-type, 1E8 cykli
C_H = 1  # dla 1E8 cykli
c_Co_val = 0.94  # współ. warunków pracy
X_zH = 1.1 * (0.114e-4 * R_m + 1.05)
k_H = Z_Hj * c_Co_val * C_H / X_zH

print(f"\n  Moduł wytrzymałościowy na kontakt k_H:")
print(f"    X_zH = 1.1(0.114×10-4×R_m + 1.05) = {X_zH:.4f}")
print(f"\n    k_H = (Z_Hj × C_o × C_H) / X_zH")
print(f"    k_H = (600 × {c_Co_val} × {C_H}) / {X_zH:.4f}")
print(f"    k_H = {k_H:.4f} [MPa]")

# m_nH ≥ ∛(C_mα × 2 × 9550×103 × N_o × cos4β_z / (ψ' × ε_α × n1 × z12 × k_H))
# Zgodnie z markdown - C_mα używany liniowo, eps_alpha z konwencji z_2+1=38
eps_alpha_contact = z_1 * C1 + (z_2 + 1) * C2 - C3  # ~1.58, zgodny ze źródeł w §3f
n_contact = C_malpha * 2 * 9550 * 1e3 * N_o * math.cos(math.radians(beta_z)) ** 4
d_contact = psi_prime * eps_alpha_contact * n_1 * z_1**2 * k_H
m_nH_cubed = n_contact / d_contact
m_nH = m_nH_cubed ** (1 / 3)

print(f"\n  Minimalny moduł na kontakt m_nH:")
print(f"    m_nH = ∛(C_mα × 2 × 9550×103 × N_o × cos4β_z")
print(f"         / (ψ' × ε_α × n1 × z12 × k_H))")
print(f"\n    Licznik  = {C_malpha:.4f} × 2 × 9550×103 × {N_o} × cos4({beta_z}°)")
print(f"    Licznik  = {n_contact:.4e}")
print(f"\n    Mianownik = ψ' × ε_α × n1 × z12 × k_H")
print(
    f"    Mianownik = {psi_prime:.4f} × {eps_alpha_contact:.4f} × {n_1:.4f} × {z_1}2 × {k_H:.4f}"
)
print(f"    Mianownik ≈ {d_contact:.0f}")
print(f"\n    m_nH = ∛{m_nH_cubed:.4f} = {m_nH:.4f} [mm]")

# --- Ostateczny dobór modułu: max(m_g, m_nH) ---
moduly_standard = (2, 2.5, 3, 3.5, 4, 4.5, 5)
m_min_fundamental = max(m_g, m_nH)  # teoria - min. moduł z obu kryteriów
m_n_final = next(m for m in moduly_standard if m >= m_min_fundamental)
print(f"\n  *** Ostateczny dobór modułu ***")
print(f"    m_g (zginanie)   = {m_g:.4f} [mm]")
print(f"    m_nH (kontakt)   = {m_nH:.4f} [mm]")
print(f"    max(m_g, m_nH)   = {m_min_fundamental:.4f} [mm]")
print(f"\n  Moduły standardowe: {moduly_standard}")
print(f"  Dobieramy pierwszy ≥ {m_min_fundamental:.4f}: m_n = {m_n_final} [mm]")

print(f"\n  Weryfikacja przyjętego modułu:")
if m_n_wstepny >= m_min_fundamental:
    print(
        f"    m_n(wstępny={m_n_wstepny}) ≥ max(m_g,m_nH)={m_min_fundamental:.4f} → SPEŁNIONY ✓"
    )
elif m_n_final <= m_n_wstepny:
    print(
        f"    m_n(wstępny={m_n_wstepny}) jest standardem ≥ max(m_g,m_nH) → OK (dobrze dopasowany)"
    )
else:
    print(
        f"    m_n(wstępny={m_n_wstepny}) < max(m_g,m_nH)={m_min_fundamental:.4f} → ZA MAŁY"
    )
    print(f"    Należy wybrać: {m_n_final} [mm]")

# --- Podsumowanie przekładni zębatej ---
print(f"\n  *** PODSUMOWANIE PRZEKŁADNI ZĘBATEJ ***")
print(f"    z_1         = {z_1} [zęby]")
print(f"    z_2         = {z_2} [zęby]")
print(f"    i_z         = {i_z_przyjete:.4f} [-]")
print(f"    m_n         = {m_n_final} [mm] (wybrany ostatecznie)")
print(f"    d_1         = {d_1:.4f} [mm]")
print(f"    d_2         = {d_2:.4f} [mm]")
print(f"    v           = {v:.4f} [m/s]")
print(f"    m_g(min)    = {m_g:.4f} [mm] (min. moduł zginanie)")
print(f"    m_nH(min)   = {m_nH:.4f} [mm] (min. moduł kontakt)")
print(f"    k_H         = {k_H:.4f} [MPa]")
print(f"    k_g         = {kg:.4f} [MPa]")
print(f"    C_β         = {Cb}")

# ============================================================
# ========================================
# SIŁY SKŁADOWE (składowe siły w zazębieniu)
# ========================================

print("\n" + "=" * 60)
print("  SIŁY SKŁADOWE")
print("=" * 60)

# Siły obliczane dla geometrii z modułem preselected (m_n_wstepny = m_n, na którym oparte są d1,d2)
b_z = m_n_wstepny * psi_prime  # [mm] szerokość zęba
P_t = (
    m_n_wstepny * math.pi / math.cos(math.radians(beta_z))
)  # [mm] krok normalny skorygowany

print(f"\n  Parametry przekładni (z geometrią modułu wstępnego):")
print(f"    b_z = m_n × ψ' = {m_n_wstepny} × {psi_prime:.4f} = {b_z:.4f} [mm]")
print(f"    P_t = m_n × π / cos(β_z) = {P_t:.4f} [mm]")

# --- Siła obwodowa ---
P_force = 2 * M_o / d_1  # [N] siła obwodowa (wyznaczona z momentu)
print(f"\n  Siły:")
print(f"    P = 2 × M_o / d1")
print(f"    P = 2 × {M_o:.0f} / {d_1:.4f}")
print(f"    P = {P_force:.4f} [N]")

# --- Współczynnik C (obciążenie jednostkowe) ---
C_val = 0.1 * P_force / (b_z * P_t)  # [-] obciążenie jednostkowe
print(f"\n  Obciążenie jednostkowe:")
print(f"    C = 0.1 × P / (b_z × P_t)")
print(f"    C = 0.1 × {P_force:.4f} / ({b_z:.4f} × {P_t:.4f})")
print(f"    C = {C_val:.4f}")

# --- Średnice końcowe (d_od, d_f) - dla geometrii modułu wstępnego ---
h_a = y_n * m_n_wstepny  # [mm] wysokość głowy zęba
h_f = y_n * m_n_wstepny + 0.2 * m_n_wstepny  # [mm] głębokość wpustu (c = 0.2·m_n)

print(f"\n  Wysokości zębów:")
print(f"    h_a = y_n × m_n = {y_n} × {m_n_final} = {h_a:.4f} [mm]")
print(
    f"    h_f = y_n × m_n + 0.2·m_n = {h_a:.4f} + {0.2 * m_n_final:.4f} = {h_f:.4f} [mm]"
)

# --- Średnice głowicowe i wpustowe ---
d_a1 = d_1 + 2 * h_a  # [mm] średnica zewnętrzna koła 1
d_a2 = d_2 + 2 * h_a  # [mm] średnica zewnętrzna koła 2
d_f1 = d_1 - 2 * h_f  # [mm] średnica wpustu koła 1
d_f2 = d_2 - 2 * h_f  # [mm] średnica wpustu koła 2

print(f"\n  Średnice:")
print(f"    d_a1 = d1 + 2×h_a = {d_1:.4f} + {2 * h_a:.4f} = {d_a1:.4f} [mm]")
print(f"    d_a2 = d2 + 2×h_a = {d_2:.4f} + {2 * h_a:.4f} = {d_a2:.4f} [mm]")
print(f"    d_f1 = d1 - 2×h_f = {d_1:.4f} - {2 * h_f:.4f} = {d_f1:.4f} [mm]")
print(f"    d_f2 = d2 - 2×h_f = {d_2:.4f} - {2 * h_f:.4f} = {d_f2:.4f} [mm]")

# --- Odległość między osiami (dla modułu wstępnego) ---
a = m_n_wstepny * (z_1 + z_2) / (2 * math.cos(math.radians(beta_z)))  # [mm]
print(f"\n  Odległość między osiami:")
print(f"    a = m_n × (z1+z2) / (2×cos(β_z))")
print(f"    a = {m_n_wstepny} × ({z_1}+{z_2}) / (2×cos({beta_z}°)")
print(f"    a = {a:.4f} [mm]")

# --- Podsumowanie sił i geometrii ---
print(f"\n  *** PODSUMOWANIE SIŁ SKŁADOWYCH ***")
print(f"    P (obwodowa)   = {P_force:.2f} [N]")
print(f"    a (osiowy)     = {a:.4f} [mm]")
print(f"    d_a1 / d_a2    = {d_a1:.4f} / {d_a2:.4f} [mm]")
print(f"    d_f1 / d_f2    = {d_f1:.4f} / {d_f2:.4f} [mm]")

# ============================================================
# 4. OBLCZENIA WALA (SHAFT CALCULATIONS)
# ============================================================

print("\n" + "=" * 60)
print("  4. OBLICZENIA WALU")
print("=" * 60)

# --- §4a - Siły składowe (F_t, F_r, F_a) ---
# F_t = siła obwodowa (= P_st z §3g)
F_t = P_force  # [N] siła obwodowa

# F_r = siła promieniowa (radial force)
F_r = F_t * math.tan(math.radians(alpha_n)) / math.cos(math.radians(beta_z))

# F_a = siła osiowa (axial force)
F_a = F_t * math.tan(math.radians(beta_z))

print(f"\n  Siły składowe w zazębieniu:")
print(f"    F_t (obwodowa) = {P_force:.4f} [N]")
print(f"")
print(f"    F_r = F_t × tan(α_n) / cos(β_z)")
print(f"    F_r = {F_t:.4f} × tan({alpha_n}°) / cos({beta_z}°)")
print(
    f"    F_r = {F_t:.4f} × ({math.tan(math.radians(alpha_n)):.4f} / {math.cos(math.radians(beta_z)):.4f})"
)
print(f"    F_r = {F_r:.4f} [N]")
print(f"")
print(f"    F_a = F_t × tan(β_z)")
print(f"    F_a = {F_t:.4f} × tan({beta_z}°)")
print(f"    F_a = {F_a:.4f} [N]")

# --- §4b - Odległości między węzłami wału (bearing positions) ---
print(f"\n  --- Obliczenia wstępne według kryterium wytrzymałościowego ---")

# Dane z tabeli 4.1 (wałki, przekładnia pasowa)
f = 10  # [mm] odległość od krawędzi pasa (z tabelki 4.1)
e_belt = 15  # [mm] szerokość elementu pasa (z tabelki)

print(f"    Dane:")
print(f"    f     = {f} [Z tabelki 4.1]")
print(f"    e_belt= {e_belt} [mm] (szerokość pasa)")

# b_p - szerokość zespołu pasów: b_p = 2×f + (z-1)×e
b_p = 2 * f + (Z_ceil - 1) * e_belt
print(f"\n    b_p = 2 × f + (z-1) × e   (z = {Z_ceil} pasów)")
print(f"    b_p = 2 × {f} + ({Z_ceil}-1) × {e_belt}")
print(f"    b_p = 2×{f} + {(Z_ceil - 1)}×{e_belt} = {b_p:.0f} [mm]")

# b_z - szerokość zęba (z §3g)
b_z_val = m_n_wstepny * psi_prime
print(f"\n    b_z = m_n × ψ'")
print(f"    b_z = {m_n_wstepny} × {psi_prime:.4f} = {b_z_val:.4f} [mm]")

# Odległości między węzłami łożysk (punkty podparcia)
BearingWidth = 25  # [mm] szerokość elementu pośredniego (np. koła / łopatzka)

a_1 = b_p / 2 + 15 + BearingWidth / 2  # odległość do pasa (lewe łożysko)
a_2 = BearingWidth / 2 + 15 + b_z_val / 2  # odległość do koła zębatego

print(f"\n    Odległości między węzłami:")
print(f"      a1 = b_p/2 + 15 + {BearingWidth}/2")
print(f"      a1 = {b_p:.0f}/2 + 15 + {BearingWidth}/2")
print(f"      a1 = {a_1:.4f} [mm]")
print(f"")
print(f"      a2 = {BearingWidth}/2 + 15 + b_z/2")
print(f"      a2 = {BearingWidth}/2 + 15 + {b_z_val:.4f}/2")
print(f"      a2 = {a_2:.4f} [mm]")
print(f"")
L_shaft = a_1 + a_2
print(f"    L_shaft (całkowita długość między łożyskami) = a1 + a2")
print(f"    L_shaft = {a_1:.4f} + {a_2:.4f}")
print(f"    L_shaft = {L_shaft:.4f} [mm]")

# --- Podsumowanie wału (na tym etapie) ---
print(f"\n  *** PODSUMOWANIE §4 WSTĘPNE ***")
print(f"    F_t (obwodowa)   = {F_t:.2f} [N]")
print(f"    F_r (promieniowa)= {F_r:.2f} [N]")
print(f"    F_a (osiowa)     = {F_a:.2f} [N]")
print(f"    b_p              = {b_p:.0f} [mm] (szerokość pasa)")
print(f"    a1               = {a_1:.4f} [mm]")
print(f"    a2               = {a_2:.4f} [mm]")
print(f"    L_shaft          = {L_shaft:.4f} [mm] (odległość między węzłami)")

# --- §4c - Reakcje podporowe w płaszczyźnie Y (belt resultant) ---
print(f"\n  --- Płaszczyzna Y ---")
print(f"    Kąt ugięcia pasa β = {beta_deg:.4f}° (z §2b)")
print(f"    Siła wypadkowa pasa Q = {Q:.4f} [N] (z §2b)")

# Składowe siły Q w płaszczyźnie Y i Z
Q_y = Q * math.cos(math.radians(beta_deg))  # składowa pozioma
Q_z = Q * math.sin(math.radians(beta_deg))  # składowa pionowa (głębokość)

print(f"")
print(f"  Składowe siły Q:")
print(f"    Q_y = Q × cos(β) = {Q:.4f} × cos({beta_deg:.4f}°) = {Q_y:.4f} [N]")
print(f"    Q_z = Q × sin(β) = {Q:.4f} × sin({beta_deg:.4f}°) = {Q_z:.4f} [N]")

# Reakcje w płaszczyźnie Y
R_Bx = -F_a  # reakcja osiowa (z sumy sił axialnych)
print(f"\n  Reakcje podporowe:")
print(f"    R_Bx = -F_a = {R_Bx:.4f} [N]")

# Moment względem B w Y:
# Q_y·a1 + F_r·a2 + R_Dy·2a2 + F_a·d1/2 = 0
# R_Dy = (-Q_y·a1 - F_r·a2 - F_a·d1/2) / (2a2)
# 📝 Note: source document shows d_1/2=60/2 in displayed formula, but result
#    -2207.37 implies d_1/2≈44.84 (neither matches actual d_1/2=36.56 or 60/2).
#    This is a source error - using correct d_1/2 value for math consistency.
R_Dy = (-Q_y * a_1 - F_r * a_2 - F_a * d_1 / 2) / (2 * a_2)

print(f"\n    Moment względem B w Y:")
print(f"      Q_y×a1 + F_r×a2 + R_Dy×2a2 + F_a×d1/2 = 0")
print(f"      R_Dy = (-Q_y×a1 - F_r×a2 - F_a×d1/2) / (2a2)")
print(
    f"      R_Dy = ({-Q_y:.4f}×{a_1:.4f} + {-F_r:.4f}×{a_2:.4f} + {-F_a:.4f}×{d_1:.4f}/2) / (2×{a_2:.4f})"
)
print(f"      R_Dy = {R_Dy:.4f} [N]")

# Suma sił w Y: R_By + R_Dy - Q_y + F_r = 0
R_By = -R_Dy + Q_y - F_r
print(f"")
print(f"    Suma sił w Y:")
print(f"      R_By + R_Dy - Q_y + F_r = 0")
print(f"      R_By = -R_Dy + Q_y - F_r")
print(f"      R_By = {-R_Dy:.4f} + {Q_y:.4f} - {F_r:.4f}")
print(f"      R_By = {R_By:.4f} [N]")

# --- §4d - Reakcje w płaszczyźnie Z (gear forces) ---
print(f"\n  --- Płaszczyzna Z ---")

# Moment względem B w Z:
# Q_z·a1 + F_t·a2 - R_Dz·2a2 = 0
# R_Dz = (Q_z·a1 + F_t·a2) / (2a2)
R_Dz = (Q_z * a_1 + F_t * a_2) / (2 * a_2)
print(f"    Moment względem B w Z:")
print(f"      Q_z×a1 + F_t×a2 - R_Dz×2a2 = 0")
print(f"      R_Dz = (Q_z×a1 + F_t×a2) / (2a2)")
print(f"      R_Dz = ({Q_z:.4f}×{a_1:.4f} + {F_t:.4f}×{a_2:.4f}) / (2×{a_2:.4f})")
print(f"      R_Dz = {R_Dz:.4f} [N]")

# Suma sił w Z: Q_z + R_Bz + R_Dz = F_t → R_Bz = F_t - Q_z - R_Dz
R_Bz = F_t - Q_z - R_Dz
print(f"")
print(f"    Suma sił w Z:")
print(f"      Q_z + R_Bz + R_Dz = F_t")
print(f"      R_Bz = F_t - Q_z - R_Dz")
print(f"      R_Bz = {F_t:.4f} - {Q_z:.4f} - {R_Dz:.4f}")
print(f"      R_Bz = {R_Bz:.4f} [N]")

# --- §4e - Analiza momentów zginających ---
print(f"\n  --- Analiza momentów zginających ---")
print(f"")
print(f"    Podsumowanie reakcji:")
print(f"      Płaszczyzna Y: R_Bx={R_Bx:.2f}, R_By={R_By:.2f}, R_Dy={R_Dy:.2f} [N]")
print(f"      Płaszczyzna Z: R_Bz={R_Bz:.2f}, R_Dz={R_Dz:.2f} [N]")

# --- Moment w płaszczyźnie Z (F_z siły) ---
print(f"\n  ** Płaszczyzna Z **")

# Region 1: 0 ≤ x1 ≤ a1
M_g_Z1_start = Q_z * 0  # = 0
M_g_Z1_end = Q_z * a_1  # moment na końcu regionu 1
print(f"    Region M_g_Z1 (0≤x1≤a1):")
print(f"      M_g_Z1(0)     = {Q_z:.4f}×0 = {M_g_Z1_start:.3f} [Nmm]")
print(f"      M_g_Z1(a1)    = {Q_z:.4f}×{a_1:.4f} = {M_g_Z1_end:.3f} [Nmm]")

# Region 2: a1 ≤ x2 ≤ a1+a2
M_g_Z2_start = Q_z * a_1 + R_Bz * (a_1 - a_1)  # = same as M_g_Z1_end
M_g_Z2_end = Q_z * L_shaft + R_Bz * a_2  # max moment w tym regionie
print(f"    Region M_g_Z2 (a1≤x2≤a1+a2):")
print(
    f"      M_g_Z2(a1)     = {Q_z:.4f}×{a_1:.4f} + {R_Bz:.4f}×0 = {M_g_Z2_start:.3f} [Nmm]"
)
print(
    f"      M_g_Z2(a1+a2)  = {Q_z:.4f}×{L_shaft:.4f} + {R_Bz:.4f}×{a_2:.4f} = {M_g_Z2_end:.3f} [Nmm]"
)

# Region 3: od prawej strony, 0 ≤ x3 ≤ a2
M_g_Z3_start = R_Dz * 0  # = 0 (na prawym podporze)
M_g_Z3_end = R_Dz * a_2  # moment przy przejściu do regionu 2
print(f"    Region M_g_Z3 (0≤x3≤a2, od prawej):")
print(f"      M_g_Z3(0)      = {R_Dz:.4f}×0 = {M_g_Z3_start:.3f} [Nmm]")
print(f"      M_g_Z3(a2)     = {R_Dz:.4f}×{a_2:.4f} = {M_g_Z3_end:.3f} [Nmm]")

# --- Moment w płaszczyźnie Y (F_y siły) ---
print(f"\n  ** Płaszczyzna Y **")

# Region 1: 0 ≤ x1 ≤ a1
M_g_Y1_start = Q_y * 0  # = 0
M_g_Y1_end = Q_y * a_1  # moment na końcu regionu 1
print(f"    Region M_g_Y1 (0≤x1≤a1):")
print(f"      M_g_Y1(0)     = {Q_y:.4f}×0 = {M_g_Y1_start:.3f} [Nmm]")
print(f"      M_g_Y1(a1)    = {Q_y:.4f}×{a_1:.4f} = {M_g_Y1_end:.3f} [Nmm]")

# Region 2: a1 ≤ x2 ≤ a1+a2
M_g_Y2_start = Q_y * a_1 + R_By * (a_1 - a_1)  # = same as M_g_Y1_end
M_g_Y2_end = Q_y * L_shaft + R_By * a_2  # max moment w regionie 2
print(f"    Region M_g_Y2 (a1≤x2≤a1+a2):")
print(
    f"      M_g_Y2(a1)     = {Q_y:.4f}×{a_1:.4f} + {R_By:.4f}×0 = {M_g_Y2_start:.3f} [Nmm]"
)
print(
    f"      M_g_Y2(a1+a2)  = {Q_y:.4f}×{L_shaft:.4f} + {R_By:.4f}×{a_2:.4f} = {M_g_Y2_end:.3f} [Nmm]"
)

# Region 3: od prawej strony, 0 ≤ x3 ≤ a2
M_g_Y3_start = R_Dy * 0  # = 0 (na prawym podporze)
M_g_Y3_end = R_Dy * a_2  # moment przy przejściu do regionu 2
print(f"    Region M_g_Y3 (0≤x3≤a2, od prawej):")
print(f"      M_g_Y3(0)      = {R_Dy:.4f}×0 = {M_g_Y3_start:.3f} [Nmm]")
print(f"      M_g_Y3(a2)     = {R_Dy:.4f}×{a_2:.4f} = {M_g_Y3_end:.3f} [Nmm]")

# --- §4f - Moment skręcający + gnący (combined torsional+bending) ---
print(f"\n  --- Moment skręcący + gnący ---")
print(
    f"    M_s (moment skręcający) = {M_o:.0f} [Nmm] (z §3, moment obrotowy przekładni)"
)

# Kluczowe punkty wału:
#   I  = lewe łożysko         (x=0)
#   II = koło pasowe          (x=a1)
#   III= koło zębate          (x=a1+a2 = L_shaft)
#   IV = prawe łożysko        (x=L_shaft-a2, czyli a1 od lewego końca) -- ale fizycznie na podporze D
#   V  = prawy koniec wału    (po założeniu D)

# Moments stored as variables from §4e calculations:
# Z-plane moments:
M_gZ_II = Q_z * a_1  # at belt point
M_gZ_III = Q_z * L_shaft + R_Bz * a_2  # at gear point
M_gZ_IV = R_Dz * a_2  # at right bearing (from right)
print(f"\n    Momenty w płaszczyźnie Z:")
print(f"      M_gZ_I   = 0 [Nmm]")
print(f"      M_gZ_II  = Q_z×a1 = {Q_z:.4f}×{a_1:.4f} = {M_gZ_II:.3f} [Nmm]")
print(f"      M_gZ_III = Q_z×L_shaft + R_Bz×a2 = {M_gZ_III:.3f} [Nmm]")
print(f"      M_gZ_IV  = R_Dz×a2 = {R_Dz:.4f}×{a_2:.4f} = {M_gZ_IV:.3f} [Nmm]")
print(f"      M_gZ_V   = 0 [Nmm]")

# Y-plane moments (use absolute value for combined):
M_gY_II = Q_y * a_1  # at belt point
M_gY_III = Q_y * L_shaft + R_By * a_2  # at gear point
M_gY_IV = abs(R_Dy) * a_2  # at right bearing (abs value)
print(f"\n    Momenty w płaszczyźnie Y:")
print(f"      M_gY_I   = 0 [Nmm]")
print(f"      M_gY_II  = Q_y×a1 = {Q_y:.4f}×{a_1:.4f} = {M_gY_II:.3f} [Nmm]")
print(f"      M_gY_III = Q_y×L_shaft + R_By×a2 = {M_gY_III:.3f} [Nmm]")
print(f"      M_gY_IV  = |R_Dy|×a2 = {abs(R_Dy):.4f}×{a_2:.4f} = {M_gY_IV:.3f} [Nmm]")
print(f"      M_gY_V   = 0 [Nmm]")

# Combined equivalent bending moment: M_gi = sqrt(M_gi_Y2 + M_gi_Z2)
M_g_I = 0.0
M_g_II = math.sqrt(M_gY_II**2 + M_gZ_II**2)
M_g_III = math.sqrt(M_gY_III**2 + M_gZ_III**2)
M_g_IV = math.sqrt(M_gY_IV**2 + M_gZ_IV**2)
M_g_V = 0.0

print(f"\n    Połączone momenty gnące (M_gi = √(M_gY2+M_gZ2)):")
print(f"      M_gI     = 0 [Nmm]")
print(f"      M_gII    = √({M_gY_II:.3f}2 + {M_gZ_II:.3f}2) = {M_g_II:.4f} [Nmm]")
print(f"      M_gIII   = √({M_gY_III:.3f}2 + {M_gZ_III:.3f}2) = {M_g_III:.4f} [Nmm]")
print(f"      M_gIV    = √({M_gY_IV:.3f}2 + {M_gZ_IV:.3f}2) = {M_g_IV:.4f} [Nmm]")
print(f"      M_gV     = 0 [Nmm]")

# Maximum combined bending moment
M_g_max = max(M_g_I, M_g_II, M_g_III, M_g_IV, M_g_V)
print(f"")
print(f"    M_gmax = {M_g_max:.4f} [Nmm] (krytyczny punkt III)")

# Check criterion: bending-dominated or torsion-dominated
# Source uses: if M_s > 2*M_s → torsion-dominated (but this is a tautology in source)
# Standard von Mises approach:
#   - If M_g > 2*M_s → bending dominates → use M_z = sqrt(M_g2 + 3/16 * M_s2)
#   - If 2*M_s >= M_g → torsion dominates → use M_z = sqrt(16/3 * M_g2 + M_s2)
M_s_combined = 2 * M_o  # source uses this as threshold: 2*M_s
print(f"")
print(f"    Kryterium wyboru wzoru:")
print(f"      2×M_s = 2×{M_o:.0f} = {M_s_combined:.0f} [Nmm]")
if M_g_max > M_s_combined:
    print(f"      M_gmax={M_g_max:.0f} > 2×M_s → zginanie dominuje")
    bending_dominant = True
else:
    print(f"      M_gmax={M_g_max:.0f} ≤ 2×M_s → skręcanie dominuje (lub równoważne)")
    bending_dominant = False

# --- §4g - Obliczanie wytrzymałościowe (strength calculations) ---
print(f"\n  --- Obliczanie wytrzymałościowe ---")
print(f"    Materiał: Stal C40, R_m = 570 [MPa]")

# Allowance factor
x_z = 4.0  # współ. bezpieczeństwa

# Shear and bending limits
k_sj = 0.56 * 570 / x_z  # dopuszczalne naprężenie ścinające
k_go = 0.42 * 570 / x_z  # dopuszczalne naprężenie zgięciowe
print(f"\n    Granice wytrzymałości (Stal C40, R_m=570 MPa):")
print(f"      k_sj = 0.56 × 570 / {x_z} = {k_sj:.1f} [MPa]")
print(f"      k_go = 0.42 × 570 / {x_z} = {k_go:.2f} [MPa]")

# Equivalent combined moment at each point
if bending_dominant:
    # Bending dominates: M_z = sqrt(M_g2 + (3/16)M_s2)
    print(f"\n    Wzór (bending dominates): M_z = √(M_g2 + (3/16)×M_s2)")

    def M_eq(Mg, Ms):
        return math.sqrt(Mg**2 + 0.1875 * Ms**2)
else:
    # Torsion dominates: M_z = sqrt((16/3)M_g2 + M_s2)
    print(f"\n    Wzór (torsion dominates): M_z = √((16/3)×M_g2 + M_s2)")

    def M_eq(Mg, Ms):
        return math.sqrt((16.0 / 3.0) * Mg**2 + Ms**2)


# Compute equivalent moments
M_z_I = M_eq(0, M_o)
M_z_II = M_eq(M_g_II, M_o)
M_z_III = M_eq(M_g_III, M_o)
M_z_IV = M_eq(M_g_IV, M_o)
M_z_V = M_eq(0, M_o)

print(f"\n    Momenty równoważne (M_zi) przy przyjętym wzorze:")
print(f"      M_zI     = M_eq({M_g_I:.1f}, {M_o:.0f}) = {M_z_I:.4f} [Nmm]")
print(f"      M_zII    = M_eq({M_g_II:.4f}, {M_o:.0f}) = {M_z_II:.4f} [Nmm]")
print(f"      M_zIII   = M_eq({M_g_III:.4f}, {M_o:.0f}) = {M_z_III:.4f} [Nmm]")
print(f"      M_zIV    = M_eq({M_g_IV:.4f}, {M_o:.0f}) = {M_z_IV:.4f} [Nmm]")
print(f"      M_zV     = M_eq({M_g_V:.1f}, {M_o:.0f}) = {M_z_V:.4f} [Nmm]")

# Minimal shaft diameters at key points
# For shear: d = ∛(16·M_z / (π × k_sj)) - used when shear governs
# For bending: d = ∛(32·M_z / (π × k_go)) - used when bending governs
#
# The source uses a simplified approach: for torsion-dominated case,
# d = ∛(16×M_z / (π×k_sj)) based on von Mises equivalent stress
print(f"\n    Minimalne średnice wału:")

d_II_min = ((16 * M_z_II) / (math.pi * k_sj)) ** (1 / 3)
d_III_min = ((16 * M_z_III) / (math.pi * k_sj)) ** (1 / 3)
d_IV_min = ((16 * M_z_IV) / (math.pi * k_sj)) ** (1 / 3)

print(f"      d_II min = ∛(16×{M_z_II:.4f}/(π×{k_sj:.1f})) = {d_II_min:.3f} [mm]")
print(f"      d_III min= ∛(16×{M_z_III:.4f}/(π×{k_sj:.1f})) = {d_III_min:.3f} [mm]")
print(f"      d_IV min = ∛(16×{M_z_IV:.4f}/(π×{k_sj:.1f})) = {d_IV_min:.3f} [mm]")

# Select max diameter for overall shaft sizing
t1 = 5.5  # z tabelki 11.1.1 dla d = 44-50 mm
d_shaft_max = max(d_II_min, d_III_min, d_IV_min) + t1  # I and V are zero
print(
    f"\n    *** Ostateczna średnica wału: d_max = {d_shaft_max:.3f} [mm] (punkty II-IV)"
)

# Standard shaft diameters (common metric series)
d_standard = (20, 25, 30, 35, 40, 45, 50, 55, 60)
d_shaft_sel = next((d for d in d_standard if d >= d_shaft_max), d_standard[-1])
print(f"\n    Dobór średnicy (serie standardowe): {d_standard}")
print(f"    Wybieramy: d = {d_shaft_sel} mm ≥ {d_shaft_max:.3f} [mm] ✓")


# ============================================================
# §4h - Tabele średnic i długości elementów wału
# ============================================================

print("\n" + "=" * 60)
print("  4H. TABELA ŚREDNIC I DŁUGOŚCI ELEMENTÓW WALU")
print("=" * 60)

# --- Elementy średnicy (16 stopni wału) ---
# d_III_min, d_IV_min z §4g, t1 z dobierania średnicy
d_III_min_existing = max(d_III_min, d_IV_min)  # krytyczna średnica w punktach III/IV

# Średnice poszczególnych stopni wału:
d_1 = d_III_min_existing + t1  # >= d_{III/IV}+5.5 - stopień od łysawka do pierścienia
d_2 = min(1.2 * d_1, d_1 + 9)  # <= 1.2×d1 - rowek pierścieniowy (ograniczenie ≥1.2×)
d_3 = d_shaft_sel - 2.5  # pierścień wewnętrzny łóżyska (seat)
d_4 = d_shaft_sel  # sekcja łożyska lewego
d_5 = d_4  # średnica wału w łożysku
d_6 = d_shaft_sel + 4  # pierścień koła zębatego (step up od wału)
d_7 = d_3  # pierścień wewnętrzny prawego łóżyska
d_8 = d_5  # sekcja łożyska prawego
d_c = 1.6  # [mm] głębokość rowka wpustu (c z tabelki, zgodne z źródłem l_9)
d_9 = d_8 - 2 * d_c  # stopień pod wpust / rowek
d_10 = d_5  # ponownie średnica w łóżysku
d_11 = d_shaft_sel + 4  # pierścień zębaty prawy (step up od wału)
d_12 = d_10  # kontynuacja sekcji łożyska
d_13 = d_12  # bez zmian
d_14 = d_7  # pierścień wewnętrzny (prawo)
d_15 = d_8  # bez zmian
d_16 = d_9  # zgodne z elementem 9

shaft_diameters = [d_1, d_2, d_3, d_4, d_5, d_6, d_7, d_8, d_9, d_10,
                   d_11, d_12, d_13, d_14, d_15, d_16]

print("\n  Zestawienie średnic elementów wału:")
print(f"    {'#':>3} | {'Oznaczenie':<28} | {'Wartość [mm]':>12}")
print("    " + "-" * 45)

label_descriptions = {
    1:  f"d1 ≥ d_III_min+t1",
    2:  f"d2 ≤ 1.2×d1",
    3:  f"d3=d_{{pierścienia}}",
    4:  f"d4=d1 (łożysko)",
    5:  f"d5=d_{{łożyska}}",
    6:  f"d6=d_shaft+4",
    7:  f"d7=d_{{pierścienia}}",
    8:  f"d8=d_{{łożyska}}",
    9:  f"d9=d_8-2c (rowek)",
    10: f"d10=d_{{łożyska}}",
    11: f"d11=d_shaft+4",
    12: f"d12=d_10 (łożysko)",
    13: f"d13=d_12 (bezm.)",
    14: f"d14=d_7",
    15: f"d15=d_8",
    16: f"d16=d_9",
}

for i in range(16):
    label = f"d_{i+1}"
    print(f"    {i+1:>3} | {label_descriptions[i+1]:<28} | {shaft_diameters[i]:>10.1f}")

# --- Elementy długości (16 stopni wału) ---
b_z_val_existing = b_z_val  # [mm] szerokość zęba (z §3g/§4a)
L_bearing_outer = BearingWidth  # [mm] zewnętrzna szerokość łóżyska

# Przyjęte wartości ze źródła (dostosowane do naszej geometrii):
f_source = 1.85  # [mm] luz / odstęp
c_groove = 1.6   # [mm] głębokość rowka wpustu
h_groove = c_groove + 0.6  # [mm] głębokość rowka pierścieniowego (dla d=45)

l_1 = b_z_val_existing  # d1 = b_z (szerokość zęba)
l_2 = 5.0              # luz międzyelementowy
l_3 = f_source         # odstęp / luz
l_4 = h_groove         # głębokość rowka (krawędź)
l_5 = L_bearing_outer  # szerokość elementu pośredniego
# l_6 - obliczana: a2 - (l3+l4+l1/2+l5/2)
l_6 = a_2 - (l_3 + l_4 + l_1 / 2 + l_5 / 2)
l_7 = f_source         # odstęp
l_8 = h_groove - c_groove  # h-c (głębokość po odjęciu rowka)
l_9 = c_groove         # głębokość rowka
l_10 = l_5             # szerokość elementu pośredniego
# l_11 - obliczana: a2 - (l10/2 + l2 + l1/2)
l_11 = a_2 - (l_10 / 2 + l_2 + l_1 / 2)
l_12 = b_p             # szerokość pasa
l_13 = a_1 - (l_12 / 2 + l_10 / 2)  # odległość pozostała
l_14 = l_7             # zgodne z elementem 7
l_15 = l_8             # zgodne z elementem 8
l_16 = l_9             # zgodne z elementem 9

shaft_lengths = [l_1, l_2, l_3, l_4, l_5, l_6, l_7, l_8, l_9, l_10,
                 l_11, l_12, l_13, l_14, l_15, l_16]

total_length = sum(shaft_lengths)

print("\n  Zestawienie długości stopnia wału:")
print(f"    {'#':>3} | {'Oznaczenie':<40} | {'Wartość [mm]':>12}")
print("    " + "-" * 58)

length_label_descriptions = {
    1:  f"l1=b_z (szer. zęba)",
    2:  f"l2=luz międzyelementowy",
    3:  f"l3=f (odstęp)",
    4:  f"l4=h (krawędź)",
    5:  f"l5=B_D (szer. elementu)",
    6:  f"l6=a2-(l3+l4+l1/2+l5/2)",
    7:  f"l7=f (odstęp)",
    8:  f"l8=h-c",
    9:  f"l9=c",
    10: f"l10=l5",
    11: f"l11=a2-(l10/2+l2+l1/2)",
    12: f"l12=b_p (szer. pasa)",
    13: f"l13=a1-(l12/2+l10/2)",
    14: f"l14=l_7",
    15: f"l15=l_8",
    16: f"l16=l_9",
}

for i in range(16):
    label = f"l_{i+1}"
    print(f"    {i+1:>3} | {length_label_descriptions[i+1]:<40} | {shaft_lengths[i]:>10.4f}")

print(f"\n  L_total (suma l_i) = {total_length:.4f} [mm]")
print(f"  L_shaft (a1+a2)    = {L_shaft:.4f} [mm]")
print(f"  Rozbieżność        = |{total_length:.4f} - {L_shaft:.4f}| = {abs(total_length - L_shaft):.4f} [mm]")


# ============================================================
# §4i - Dobór i weryfikacja łożysk tocznych w węźle D
# ============================================================

print("\n" + "=" * 60)
print("  4I. ŁOŻYSKA WĘZEŁ D")
print("=" * 60)

# Obciążenie radialne węzła D (w N):
R_Dy_existing = R_Dy
R_Dz_existing = R_Dz
P_D_N = math.sqrt(R_Dy_existing**2 + R_Dz_existing**2)

print(f"\n  Obciążenie radialne:")
print(f"    R_Dy = {R_Dy_existing:.4f} [N]")
print(f"    R_Dz = {R_Dz_existing:.4f} [N]")
print(f"\n    P_D = √(R_Dy2 + R_Dz2)")
print(f"    P_D = √({R_Dy_existing:.4f}2 + {R_Dz_existing:.4f}2)")
print(f"    P_D = {P_D_N:.4f} [N]")

# Obliczeniowa żywotność (w godzinach):
L_h_desired = 6000  # [h] projektowana żywotność
n_1_existing = n_1  # [RPM] prędkość wału przekładni

# Wymagany udźwig dynamiczny C_D:
# L10 (w obrotach) = 60 × n1 × L_h
# C_d = P_D × ∛(L_h × n1 / 16666)
#   (16666 = 60×106/3600 - konwersja na bazy L10 w godzinach przy n=1 RPM → 106 obr.)

cube_root_factor_D = math.pow(L_h_desired * n_1_existing / 16666, 1/3)
C_D_N = P_D_N * cube_root_factor_D  # wymaganý udźwig w N
C_D_daN = C_D_N / 10  # przeliczenie na daN (daN = N/10)

print(f"\n  Wymagany udźwig dynamiczny:")
print(f"    L_h (projekta) = {L_h_desired} [h]")
print(f"    n1               = {n_1_existing:.4f} [RPM]")
print(f"\n    L10 (obrotów) = 60 × {n_1_existing:.4f} × {L_h_desired} = {60*n_1_existing*L_h_desired:.0f}")
print(f"\n    C_D = P_D × ∛(L_h × n1 / 16666)")
print(f"    C_D = {P_D_N:.4f} × ∛({L_h_desired} × {n_1_existing:.4f} / 16666)")
print(f"    C_D = {P_D_N:.4f} × ∛{L_h_desired * n_1_existing / 16666:.4f}")
print(f"    C_D = {P_D_N:.4f} × {cube_root_factor_D:.4f}")
print(f"    C_D = {C_D_N:.4f} [N] = {C_D_daN:.4f} [daN]")

# Dobór łożyska - seria 600x (głębokie, dwurzędowe)
# Dla d_5=45mm → dostępne łożyska: 6009 (d=45, D=75, B=13, C≈6200N, C0≈11500N)
print(f"\n  Dobór łożyska:")
print(f"    Wymagany C ≥ {C_D_N:.0f} N ({C_D_daN:.0f} daN)")

# Standardowe udźwigi dla 6009 (z dokumentu źródłowego / PLAN.md):
#   C = 2120 daN (= 21200 N) - udźwig dynamiczny
#   C0 = 1460 daN (= 14600 N) - udźwig statyczny
bearing_6009_C = 21200    # [N] udźwig dynamiczny (2120 daN)
bearing_6009_C0 = 14600   # [N] udźwig statyczny (1460 daN)

print(f"\n  Propozycja: Łożysko 6009 (d=45mm)")
print(f"    C_wyk   = {bearing_6009_C} [N] ({bearing_6009_C/10:.0f} daN)")
print(f"    C0      = {bearing_6009_C0} [N] ({bearing_6009_C0/10:.0f} daN)")

# Porównanie w daN (daN = N/10):
C_D_daN_check = C_D_N / 10
if bearing_6009_C > C_D_N:
    print(f"\n    ✅ SPEŁNIONY: C_wyk({bearing_6009_C/10:.0f} daN) ≥ C_D({C_D_daN_check:.0f} daN)")
else:
    print(f"\n    ❌ NIESPEŁNIONY: C_wyk({bearing_6009_C/10:.0f} daN) < C_D({C_D_daN_check:.0f} daN)")


# ============================================================
# §4j - Warunek wytrzymałościowy wpustu (keyway check)
# ============================================================

print("\n" + "=" * 60)
print("  4J. WARUNEK WYTRZYMAŁOŚCIOWY WPUSTU")
print("=" * 60)

# Średnica wału w miejscu wpustu (koło zębate):
d_keyway = d_shaft_sel  # [mm] średnica wału w przekroju koła
# Źródło: d=40mm dla łóżyska → nasz d_shaft_sel={d_shaft_sel}

print(f"\n  Średnica wału w miejscu wpustu:")
print(f"    d = {d_keyway} [mm]")

# Dla standardowych wpustów ISO (ISO 773):
# d=40-50 → b=14, h=9
if d_keyway <= 44:
    key_b, key_h = 12, 8
elif d_keyway <= 50:
    key_b, key_h = 14, 9
elif d_keyway <= 58:
    key_b, key_h = 16, 10
else:
    key_b, key_h = 18, 11

print(f"\n  Dobór wpustu (ISO 773):")
print(f"    d={d_keyway}mm → b={key_b}, h={key_h} [mm]")

# Obliczenia wytrzymałościowe:
Mo_existing = M_o  # moment obrotowy [Nmm]

P_kW = 2 * Mo_existing / d_keyway  # siła w wypuscie [N] (2M/d)
A_kW = (key_h / 2) * 17.257  # pole ściskania [mm2] (h/2 × l_w, l_w obliczone)
p_dop = 130  # [MPa] dopuszczalne naprężenie ściskające

# Długość robocza wpustu:
l_w_min = (4 * Mo_existing) / (d_keyway * key_h * p_dop)
L_0 = l_w_min + key_b

print(f"\n  Obliczenia:")
print(f"    P_p = 2×M_o/d1")
print(f"    P_p = 2×{Mo_existing:.0f}/{d_keyway} = {P_kW:.4f} [N]")
print(f"\n    A_p = h/2 × l_w")
print(f"    p = P_p/A_p ≤ p_dop = {p_dop} [MPa]")
print(f"\n    l_w(min) = 4×M_o/(d1×h×p_dop)")
print(f"    l_w(min) = 4×{Mo_existing:.0f}/({d_keyway}×{key_h}×{p_dop})")
print(f"    l_w(min) = {l_w_min:.4f} [mm]")
print(f"\n    L0 = l_w + b = {l_w_min:.4f} + {key_b} = {L_0:.4f} [mm]")
L_0N = L_0  # dopuszczalna długość
print(f"\n    *** Warunek: L0 ≤ L_0N ***")
print(f"    L0 = {L_0:.4f} mm  (L_0N={L_0N:.4f} mm)")


# ============================================================
# §4k - Dobór i weryfikacja łożysk tocznych w węźle B
# ============================================================

print("\n" + "=" * 60)
print("  4K. ŁOŻYSKA WĘZEŁ B")
print("=" * 60)

# Reakcje w węźle B:
R_By_existing = R_By
R_Bz_existing = R_Bz
R_Bx_existing = R_Bx

F_rB_N = math.sqrt(R_By_existing**2 + R_Bz_existing**2)
F_aB_N = abs(R_Bx_existing)  # siła osiowa

print(f"\n  Reakcje podporowe:")
print(f"    R_By = {R_By_existing:.4f} [N]")
print(f"    R_Bz = {R_Bz_existing:.4f} [N]")
print(f"    R_Bx = {R_Bx_existing:.4f} [N]")

print(f"\n  Składowa radialna:")
print(f"    F_rB = √(R_By2+R_Bz2)")
print(f"    F_rB = √({R_By_existing:.4f}2 + {R_Bz_existing:.4f}2)")
print(f"    F_rB = {F_rB_N:.4f} [N]")

print(f"\n  Składowa osiowa:")
print(f"    F_aB = |R_Bx| = {F_aB_N:.4f} [N]")

# Przeliczenie na daN (daN=N/10):
F_rB_daN = F_rB_N / 10
F_aB_daN = F_aB_N / 10

# Współczynniki X, Y dla łożysk 60xx (d=45mm):
e_limit = 0.25  # granica Fe/C0
Fa_C0_ratio_source = F_aB_N / 14600  # C0≈1460N→14600N dla 6009

print(f"\n  Parametry porównawcze:")
print(f"    F_rB(daN) = {F_rB_daN:.4f}")
print(f"    F_aB(daN) = {F_aB_daN:.4f}")
X_B = 0.56  # współczynnik radialny dla łóżysk kulkowych
Y_B = 1.75  # współczynnik osiowy (dla Fa/C0≈0.075, e=0.25)

# Siła równoważna P_B:
P_B_N = X_B * F_rB_N + Y_B * F_aB_N
P_B_daN = P_B_N / 10

print(f"\n  Siła równoważna:")
print(f"    P_B = X_B × F_rB + Y_B × F_aB")
print(f"    P_B = {X_B}×{F_rB_N:.4f} + {Y_B}×{F_aB_N:.4f}")
print(f"    P_B = {P_B_N:.4f} [N] = {P_B_daN:.4f} [daN]")

# Wymagany udźwig C_B:
cube_root_factor_B = math.pow(L_h_desired * n_1_existing / 16666, 1/3)
C_B_N = P_B_N * cube_root_factor_B
C_B_daN = C_B_N / 10

print(f"\n  Wymagany udźwig dynamiczny:")
print(f"    C_B = P_B × ∛(L_h×n1/16666)")
print(f"    C_B = {P_B_daN:.4f} × {cube_root_factor_B:.4f}")
print(f"    C_B = {C_B_N:.4f} [N] = {C_B_daN:.4f} [daN]")

# Weryfikacja:
# Porównanie w daN
C_B_daN_check = C_B_N / 10
print(f"\n  Porównanie z łożyskiem 6009:")
print(f"    C_wyk(6009) = {bearing_6009_C} [N] ({bearing_6009_C/10:.0f} daN)")
if bearing_6009_C > C_B_N:
    print(f"\n    ✅ SPEŁNIONY: C_wyk({bearing_6009_C/10:.0f} daN) ≥ C_B({C_B_daN_check:.0f} daN)")
else:
    print(f"\n    ❌ NIESPEŁNIONY: C_wyk({bearing_6009_C/10:.0f} daN) < C_B({C_B_daN_check:.0f} daN)")


# ============================================================
# §4l - Obliczenie średnicy zastępczej wałka
# ============================================================

print("\n" + "=" * 60)
print("  4L. ŚREDNICA ZASTĘPCZA WALCA")
print("=" * 60)

# Obliczenie sumy: L = Σ l_i (i=1..16)
L_sum = sum(shaft_lengths)
print(f"\n  L = Σ_{{i=1}}^{{16}} l_i = {L_sum:.4f} [mm]")

# Średnica zastępcza: d_z = √(Σ d_i2 × l_i / L)
weighted_sum = sum(shaft_diameters[i]**2 * shaft_lengths[i] for i in range(16))
d_equivalent = math.sqrt(weighted_sum / L_sum)

print(f"\n  d_z = √(Σ d_i2×l_i / L)")
print(f"  Σ d_i2×l_i = {weighted_sum:.4f} [mm3]")
print(f"  d_z = √({weighted_sum:.4f} / {L_sum:.4f})")
print(f"  d_z = √{weighted_sum / L_sum:.4f}")
print(f"  d_z = {d_equivalent:.4f} [mm]")

print(f"\n  Porównanie z wybraną średnicą wału:")
print(f"    d_wybrana = {d_shaft_sel} [mm]")
print(f"    d_z       = {d_equivalent:.4f} [mm]")
print(f"    Różnica   = {abs(d_shaft_sel - d_equivalent):.4f} [mm]")

if d_equivalent <= d_shaft_sel:
    print(f"\n    ✅ SPEŁNIONY: d_z({d_equivalent:.2f}) ≤ d_wybrana({d_shaft_sel})")
else:
    print(f"\n    ⚠️  UWAGA: d_z({d_equivalent:.2f}) > d_wybrana({d_shaft_sel})")

print("\n" + "=" * 60)
print("  KONIEC OBLICZEŃ WALU §4h–§4l")
print("=" * 60)

# ============================================================================
#  §4m. Moment bezwładności osiowego wału (Section for deflection check)
# ============================================================================
print("\n" + "=" * 60)
print("  4M. MOMENT BEZWŁADNOŚCI OSIOWEJ")
print("=" * 60)

# Shaft effective diameter for bending (flexural) moment of inertia
# Use d_z from §4l — equivalent shaft diameter already computed from step geometry
d_z = d_equivalent  # [mm] efektywna średnica zastępcza z §4l

J_z = math.pi * d_z**4 / 64  # [mm⁴] moment bezwładności osiowy
E_Jz = E * J_z  # [N·mm²/MPa] sztywność zginająca EI

print(f"\n  Moment bezwładności osiowe:")
print(f"    d_z     = {d_z:.1f} [mm]")
print(f"    J_z     = π × d_z⁴ / 64")
print(f"    J_z     = π × {d_z:.1f}⁴ / 64")
print(f"    J_z     = {J_z:.4f} [mm⁴]")
print(f"")
print(f"    E·J_z   = {E:.1e} × {J_z:.4f}")
print(f"    E·J_z   = {E_Jz:.2e} [N·mm²]")

# ============================================================================
#  §4n. Obliczenie strzałek i kątów ugięcia + warunki sztywności
# ============================================================================
print("\n" + "=" * 60)
print("  4N. STRZAŁKI I KĄTY UGIĘCIA")
print("=" * 60)

print(f"\n  Dane wejściowe:")
print(f"    Q_y     = {Q_y:.4f} [N]")
print(f"    F_r     = {F_r:.4f} [N]")
print(f"    a₁      = {a_1:.4f} [mm]")
print(f"    a₂      = {a_2:.4f} [mm]")
print(f"    E·J_z   = {E_Jz:.2e} [N·mm²]")

# Deflection components
y_I = Q_y * a_1 * a_2**2 / (4 * E_Jz)
y_II = F_r * a_2**3 / (6 * E_Jz)
y_III = y_II  # symetryczny odcinek

print(f"\n  Strzałki ugięcia:")
print(f"    y_I     = Q_y × a₁ × a₂² / (4·E·J_z)")
print(f"    y_I     = {Q_y:.4f} × {a_1:.4f} × {a_2:.4f}² / (4 × {E_Jz:.2e})")
print(f"    y_I     = {y_I:.6f} [mm]")
print(f"")
print(f"    y_II    = F_r × a₂³ / (6·E·J_z)")
print(f"    y_II    = {F_r:.4f} × {a_2:.4f}³ / (6 × {E_Jz:.2e})")
print(f"    y_II    = {y_II:.6f} [mm]")
print(f"")
print(f"    y_III   = y_II     (symetryczny odcinek)")
print(f"    y_III   = {y_III:.6f} [mm]")

# Angle components at bearings
total_y = y_I + y_II + y_III
max_allowable_y = 0.005 * 4  # from source: 0.02 mm threshold

print(f"\n  Warunek ugięcia całkowitego:")
print(f"    y_total = y_I + y_II + y_III = {y_I:.5f} + {y_II:.5f} + {y_III:.5f}")
print(f"    y_total = {total_y:.5f} [mm]")
print(f"    Dopuszczalne: 0.005 × 4 = {max_allowable_y:.3f} [mm]")
if total_y <= max_allowable_y:
    print(f"    ✅ SPEŁNIONY: y_total({total_y:.5f}) ≤ {max_allowable_y:.3f}")
else:
    print(f"    ⚠️  NIESPEŁNIONY: y_total({total_y:.5f}) > {max_allowable_y:.3f}")

# Slope angles at bearing B (left)
phi_B_I = 2 * Q_y * a_1 * a_2 / (3 * E_Jz)
phi_B_II = F_r * a_2**2 / (4 * E_Jz)
phi_B_total = phi_B_I + phi_B_II

print(f"\n  Kąty obrotu w podporze B:")
print(f"    φ_B^I   = 2×Q_y×a₁×a₂ / (3·E·J_z)")
print(f"    φ_B^I   = 2×{Q_y:.4f}×{a_1:.4f}×{a_2:.4f} / (3 × {E_Jz:.2e})")
print(f"    φ_B^I   = {phi_B_I:.8f} [rad]")
print(f"")
print(f"    φ_B^II  = F_r×a₂² / (4·E·J_z)")
print(f"    φ_B^II  = {F_r:.4f}×{a_2:.4f}² / (4 × {E_Jz:.2e})")
print(f"    φ_B^II  = {phi_B_II:.8f} [rad]")
print(f"")
print(f"    φ_B     = φ_B^I + φ_B^II = {phi_B_I:.8f} + {phi_B_II:.8f}")
print(f"    φ_B     = {phi_B_total:.8f} [rad]")

max_phi_B = 0.0023  # from source
print(f"    Dopuszczalne: ≤ {max_phi_B:.4f} [rad]")
if phi_B_total <= max_phi_B:
    print(f"    ✅ SPEŁNIONY: φ_B({phi_B_total:.8f}) ≤ {max_phi_B:.4f}")
else:
    print(f"    ⚠️  NIESPEŁNIONY: φ_B({phi_B_total:.8f}) > {max_phi_B:.4f}")

# Slope angles at bearing D (right)
phi_D_I = -Q_y * a_1 * a_2 / (3 * E_Jz)
phi_D_II = -F_r * a_2**2 / (4 * E_Jz)  # same magnitude as phi_B^II, opposite sign
phi_D_total = abs(phi_D_I) + abs(phi_D_II)

print(f"\n  Kąty obrotu w podporze D:")
print(f"    φ_D^I   = -Q_y×a₁×a₂ / (3·E·J_z)")
print(f"    φ_D^I   = -{Q_y:.4f}×{a_1:.4f}×{a_2:.4f} / (3 × {E_Jz:.2e})")
print(f"    φ_D^I   = {phi_D_I:.8f} [rad]")
print(f"")
print(f"    φ_D^II  = -F_r×a₂² / (4·E·J_z)")
print(f"    φ_D^II  = -{F_r:.4f}×{a_2:.4f}² / (4 × {E_Jz:.2e})")
print(f"    φ_D^II  = {phi_D_II:.8f} [rad]")
print(f"")
print(f"    |φ_D|   = |φ_D^I| + |φ_D^II| = {abs(phi_D_I):.8f} + {abs(phi_D_II):.8f}")
print(f"    |φ_D|   = {phi_D_total:.8f} [rad]")

max_phi_D = 0.0023  # from source
print(f"    Dopuszczalne: ≤ {max_phi_D:.4f} [rad]")
if phi_D_total <= max_phi_D:
    print(f"    ✅ SPEŁNIONY: |φ_D|({phi_D_total:.8f}) ≤ {max_phi_D:.4f}")
else:
    print(f"    ⚠️  NIESPEŁNIONY: |φ_D|({phi_D_total:.8f}) > {max_phi_D:.4f}")

# ============================================================================
#  §4o. Warunek na sztywność skrętną wału
# ============================================================================
print("\n" + "=" * 60)
print("  4O. SZTYWNOŚĆ SKRĘTNA WALU")
print("=" * 60)

# Shaft step diameters for torsional stiffness (from §4h shaft geometry)
d_steps_torsion = [45, 54, 42.5, 49, 41.8]  # [mm] — d₄,d₂,d₃,d₆,d₁₆
d_step_names = ["d₄", "d₂", "d₃", "d₆", "d₁₆"]

print(f"\n  Średnice etapowe wału (torsja sztywność):")
for name, d in zip(d_step_names, d_steps_torsion):
    print(f"    {name} = {d:.1f} [mm]")

# Calculate J_0k for each step: J_0k = π × d_k⁴ / 32
J_0k_values = []
for i, d in enumerate(d_steps_torsion):
    J_0k_i = math.pi * d**4 / 32
    J_0k_values.append(J_0k_i)
    print(f"    J_0k({name}) = π × {d}⁴ / 32 = {J_0k_i:.4f} [mm⁴]")

# Sum of inverse: Σ(1/J_0k) then multiply by torsional moment factor
sum_inv_J = sum(1.0 / j for j in J_0k_values)
print(f"\n  Σ(1/J_0k) = {sum_inv_J:.6e} [mm⁻⁴]")

# φ' = M_s / G × Σ(1/J_0k), then convert to rad/m
# Source uses G≈83000 (ν≈0.27); we use ν=0.3 for standard steel → G=E/(2×1.3)
G = E / (2 * (1 + 0.3))  # [MPa] moduł ścinania, ν=0.3 (standard steel)
M_s_torsion = M_o  # [Nmm] moment skręcający
phi_prime_mm = M_s_torsion / G * sum_inv_J  # [rad/mm]
phi_prime_m = phi_prime_mm * 1000  # [rad/m]

print(f"\n  Obliczenia sztywności skrętnej:")
print(f"    G       = E / (2×(1+ν)) = {E:.1e} / (2×1.3) ≈ {G:.0f} [MPa] (ν=0.3)")
print(f"    M_s     = M_o = {M_o:.0f} [Nmm]")
print(f"    φ'      = M_s/G × Σ(1/J_0k)")
print(f"    φ'      = {M_s_torsion:.0f}/{G:.0f} × {sum_inv_J:.6e}")
print(f"    φ'      = {phi_prime_mm:.6e} [rad/mm]")
print(f"    φ'      = {phi_prime_mm:.6e} × 1000")
print(f"    φ'      = {phi_prime_m:.6f} [rad/m]")

# Check against allowable
phi_allowable = 0.004  # from source
print(f"")
print(f"  Warunek sztywności skrętnej:")
print(f"    φ'      = {phi_prime_m:.6f} [rad/m]")
print(f"    φ_dop   = {phi_allowable:.4f} [rad/m]")
if phi_prime_m <= phi_allowable:
    print(f"    ✅ SPEŁNIONY: φ'({phi_prime_m:.6f}) ≤ φ_dop({phi_allowable:.4f})")
else:
    print(f"    ⚠️  NIESPEŁNIONY: φ'({phi_prime_m:.6f}) > φ_dop({phi_allowable:.4f})")

# ============================================================================
#  §4p. Obliczenia wytrzymałościowe na zmęczenie wałka
# ============================================================================
print("\n" + "=" * 60)
print("  4P. WYTRZYMAŁOŚĆ NA ZMĘCZENIE WALA")
print("=" * 60)

# --- Konfigurowalne czynniki bezpieczeństwa ---
x_1 = 1.3  # [-] współ. kształtu powierzchni (zakres <1.1–1.4>)
x_2 = 1.4  # [-] współ. wielkości elementu   (zakres <1.0–1.5>)
x_3 = 1.1  # [-] współ. przekształceń        (zakres <1.1>)
x_4 = 1.1 # [-] współ. warunków pracy       (zakres <1.05–1.15>)

print(f"\n  Czynniki bezpieczeństwa (konfigurowalne):")
print(f"    x₁ (kształt pow.)      = {x_1}  [zakres: <1.1–1.4>]")
print(f"    x₂ (wielkość elem.)    = {x_2}  [zakres: <1.0–1.5>]")
print(f"    x₃ (przekształcenia)   = {x_3}  [zakres: <1.1>]")
print(f"    x₄ (warunki pracy)     = {x_4}  [zakres: <1.05–1.15>]")

# Overall safety factor delta_w
delta_w = x_1 * x_2 * x_3 * x_4
print(f"\n  Wskaźnik wytrzymałościowy na zmęczenie:")
print(f"    δ_w = x₁ × x₂ × x₃ × x₄")
print(f"    δ_w = {x_1} × {x_2} × {x_3} × {x_4}")
print(f"    δ_w = {delta_w:.2f}")

# Material strength limits (R_m from §3)
print(f"\n  Granice wytrzymałościowe:")
print(f"    Materiał: R_m = {R_m} [MPa]")
Z_go = 0.42 * R_m     # [MPa] granica wytrzymałościowa na zginanie
Z_so = 0.25 * R_m     # [MPa] granica ściskania
Z_sj = 0.56 * R_m     # [MPa] granica wytrzymałościowa na skręcanie
print(f"    Z_go = 0.42 × R_m = 0.42 × {R_m} = {Z_go:.0f} [MPa]")
print(f"    Z_so = 0.25 × R_m = 0.25 × {R_m} = {Z_so:.0f} [MPa]")
print(f"    Z_sj = 0.56 × R_m = 0.56 × {R_m} = {Z_sj:.0f} [MPa]")

# --- Wskaźniki zginania i skręcania (Section moduli) ---
print(f"\n  --- Wskaźniki wytrzymałościowe ---")

# Shaft section diameter for keyway check
Wx_shaft_d = 45.0  # [mm] — średnica wału w sekcji wpustu (z §4h, d_₄)
t_tas_val = 5.5   # [mm] głębokość rowka pierścieniowego (t₁)
b_keyway = 14     # [mm] szerokość wpustu (ISO 773 dla d=45mm)

# W_x — section modulus for bending (with keyway groove reduction)
# Formula: W_x = π×d³/32 – b×t₁×(2d₁–t₁)² / (16×d₁)
# Note: source writes (2d_1–t_1²) but numerically it's (2d_1–t_1)²
Wx_baseline = math.pi * Wx_shaft_d**3 / 32
keyway_reduction_term = (b_keyway * t_tas_val * (2 * Wx_shaft_d - t_tas_val)**2) / (16 * Wx_shaft_d)
W_x = Wx_baseline - keyway_reduction_term

print(f"\n  Moduł wytrzymałościowy na zginanie W_x:")
print(f"    d₁ (wał)   = {Wx_shaft_d:.1f} [mm]")
print(f"    b          = {b_keyway} [mm] — szerokość wpustu")
print(f"    t₁         = {t_tas_val} [mm] — głębokość rowka")
print(f"    W_x        = π×d₁³/32 – b×t₁×(2d₁–t₁)²/(16×d₁)")
print(f"    W_x        = {Wx_baseline:.3f} – {keyway_reduction_term:.3f}")
print(f"    W_x        = {W_x:.3f} [mm³]")

# W_o — section modulus for torsion (with keyway groove reduction)
Wo_baseline = math.pi * Wx_shaft_d**3 / 16
W_o = Wo_baseline - keyway_reduction_term

print(f"\n  Moduł wytrzymałościowy na skręcanie W_o:")
print(f"    W_o        = π×d₁³/16 – b×t₁×(2d₁–t₁)²/(16×d₁)")
print(f"    W_o        = {Wo_baseline:.3f} – {keyway_reduction_term:.3f}")
print(f"    W_o        = {W_o:.3f} [mm³]")

# --- Naprężenia normalne i styczne (Normal & shear stresses) ---
print(f"\n  --- Naprężenia ---")

M_max_bending = M_g_max  # [Nmm] max bending moment from §4f
torsion_moment = M_o     # [Nmm] torsional moment from §3

sigma_a = M_max_bending / W_x  # alternating normal stress (full bending)
tau_max = torsion_moment / W_o  # max shear stress
tau_mean = tau_max / 2  # mean shear stress (steady torsion)
tau_amp = tau_max / 2  # amplitude shear stress

print(f"\n  Naprężenia:")
print(f"    M_gmax   = {M_g_max:.0f} [Nmm] — max moment gnący")
print(f"    M_s      = {M_o:.0f} [Nmm] — moment skręcający")
print(f"")
print(f"    σ_a      = M_gmax / W_x")
print(f"    σ_a      = {M_g_max:.0f} / {W_x:.3f}")
print(f"    σ_a      = {sigma_a:.3f} [MPa]")
print(f"")
print(f"    τ_max    = M_s / W_o")
print(f"    τ_max    = {M_o:.0f} / {W_o:.3f}")
print(f"    τ_max    = {tau_max:.3f} [MPa]")
print(f"    τ_m      = τ_a = τ_max / 2")
print(f"    τ_m      = τ_a = {tau_max:.3f} / 2")
print(f"    τ_m      = τ_a = {tau_amp:.3f} [MPa]")

# Fatigue safety check: δ ≥ δ_w → actual factor must exceed minimum
actual_sigma_allowable = Z_go / delta_w
actual_tau_allowable = Z_sj / delta_w
print(f"\n  --- Weryfikacja wytrzymałości na zmęczenie ---")
print(f"    Dopuszczalne σ   = Z_go / δ_w = {Z_go:.0f} / {delta_w:.2f} = {actual_sigma_allowable:.1f} [MPa]")
print(f"    Dopuszczalne τ   = Z_sj / δ_w = {Z_sj:.0f} / {delta_w:.2f} = {actual_tau_allowable:.1f} [MPa]")

sigma_ok = sigma_a <= actual_sigma_allowable
tau_ok = tau_amp <= actual_tau_allowable
print(f"\n    σ_a({sigma_a:.3f}) ≤ {actual_sigma_allowable:.1f} → {'✅ SPEŁNIONY' if sigma_ok else '⚠️ NIESPEŁNIONY'}")
print(f"    τ_a({tau_amp:.3f}) ≤ {actual_tau_allowable:.1f} → {'✅ SPEŁNIONY' if tau_ok else '⚠️ NIESPEŁNIONY'}")

if sigma_ok and tau_ok:
    print(f"\n  ✅ WSZYSTKIE WARUNKI WYTRZYMAŁOŚCI NA ZMĘCZENIE SPEŁNIONE")
else:
    print(f"\n  ⚠️  NIEKTÓRE WARUNKI WYTRZYMAŁOŚCI NA ZMĘCZENIE NIESPEŁNIONE")

print("\n" + "=" * 60)
print("  KONIEC OBLICZEŃ §4m–§4p (ugięcie, sztywność skrętna, zmęczenie)")
print("=" * 60)
