# ========================================
# DOBÓR SILNIKA + PRZEŁOŻENIE + PASY
# ========================================
import math

N_wyj = 1.51      # Moc wyjściowa [kW]
K = 1.36          # Współczynnik bezpieczeństwa
n2 = 192          # Prędkość wału wyjściowego [obr/min]

# Sprawności
eta_p = 0.96
eta_t = 0.995
eta_z = 0.98

# Obliczenia mocy
eta_c = eta_p * (eta_t ** 2) * eta_z
N0 = (K * N_wyj) / eta_c

# Dane silnika
n_s_prime = 1440  # rzeczywiste obroty silnika [obr/min]

# === PRZEŁOŻENIE ===
i_c = n_s_prime / n2
i_p = i_c ** 0.5
i_pn = int(i_p) + 1 if i_p % 1 != 0 else int(i_p)   # zaokrąglenie w górę

# === DOBÓR PASÓW ===
Kt = 1.0
N1 = 0.68      # moc przenoszona przez jeden pas [kW] (z tabeli)
dp = 71      # średnica koła napędzającego [mm]

D_p = dp * i_pn                     # średnica koła napędzanego [mm]
A0 = (D_p + dp)                     # wstępna odległość osi (przybliżenie)
L_p = 2 * A0 + 1.57 * (D_p + dp) + (D_p - dp)**2 / (4 * A0)
Lpn = 1032
p = 0.25 * Lpn - 0.393 * (D_p + dp)
q = 0.125 * (D_p - dp)**2
A = p + math.sqrt(p**2 - q)
φ = (D_p-dp)/A
kφ = 0.93
k_l = 0.89
# Liczba pasów
Z = (N0 * Kt) / (N1 * kφ * k_l)        # kφ i kL na razie = 1 (do doprecyzowania)

print("=== WYNIKI OBLICZEŃ ===")
print(f"Moc silnika N0          = {N0:.3f} kW")
print(f"Przełożenie całkowite   = {i_c:.2f}")
print(f"Przełożenie jednej pary = {i_p:.2f} → zaokrąglono do {i_pn}\n")

print("=== DOBÓR PASÓW ===")
print(f"Średnica małego koła dp   = {dp} mm")
print(f"Średnica dużego koła Dp   = {D_p:.0f} mm")
print(f"Wstępna odległość osi A0 = {A0:.0f} mm")
print(f"Długość pasa Lp           = {L_p:.1f} mm")
print(f"wartosc kata = {φ} ")
print(f"Liczba pasów Z            = {Z:.2f}")