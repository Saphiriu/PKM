import math


N_wyj = 1.51      # Moc wyjściowa [kW]
K = 1.36
n2 = 192


eta_p = 0.96
eta_t = 0.995
eta_z = 0.98

eta_c = eta_p * (eta_t ** 2) * eta_z
N0 = (K * N_wyj) / eta_c

n_s_prime = 1440


i_c = n_s_prime / n2
i_p = i_c ** 0.5
i_pn = math.ceil(i_p)                    # zaokrąglenie w górę

# === DOBÓR PASÓW TYP A ===
Kt = 1.0
N1 = 0.68        # kW
dp = 71          # mm
Lpn = 1032      # mm - długość pasa z katalogu
k_l = 0.89
kφ = 0.93

D_p = dp * i_pn

#
p = 0.25 * Lpn - 0.393 * (D_p + dp)
q = 0.125 * (D_p - dp)**2
A = p + math.sqrt(p**2 - q)

phi = (D_p - dp) / A

# Liczba pasów
Z = (N0 * Kt) / (N1 * kφ * k_l)
Z_up = math.ceil(Z)

print("=== WYNIKI OBLICZEŃ ===")
print(f"Moc silnika N0          = {N0:.3f} kW")
print(f"i_pn        = {i_pn}\n")
print(f"i_c       = {i_c}\n")

print("=== PASY TYP A ===")
print(f"dp  (małe koło)         = {dp} mm")
print(f"Dp  (duże koło)         = {D_p} mm")
print(f"Lpn     = {Lpn} mm")
print(f"A         = {A:.1f} mm")
print(f"phi      = {phi:.3f}")
print(f"Liczba pasów Z          = {Z:.2f}  →  {Z_up} pasów")