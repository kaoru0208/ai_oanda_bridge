# Final OOS Report — SNR pick @ final_pick_eta0.5_kap0.3_lam0.05_db0.02_grid0.1

## Picked parameters
```
eta: 0.5
kap: 0.3
lam_min: 0.05
deadband: 0.02
grid: 0.1
```

## OOS summary
- windows: **5**
- wins (dSR>0): **5/5**, binomial two-sided p ≈ **0.0625**
- guard_ok_ratio: **1.00**
- SR_snr_median: **-0.376402**
- dSR_median: **0.011548**  (IQR 0.008709 → 0.014987)
- PSR_snr > 0.95 ratio: **0.40**

## Plots
- dSR by window: `oos_dsr_bars.png`
- SR(base vs SNR): `oos_sr_scatter.png`
- Equity overlay (visual): `equity_overlay.png`  *(参考：全期間可視化)*

## OOS table (head)
```
test_start   test_end   SR_base    SR_snr      dSR  PSR_base  PSR_snr  TO_base   TO_snr  guard_ok
2023-01-01 2023-06-30 -0.392650 -0.376402 0.016248  0.000008 0.000015 0.466936 0.466936      True
2023-07-01 2023-12-31  0.632946  0.641655 0.008709  1.000000 1.000000 0.548219 0.548219      True
2024-01-01 2024-06-30 -0.668118 -0.656570 0.011548  0.000000 0.000000 0.500600 0.500600      True
2024-07-01 2024-12-31 -0.609761 -0.606799 0.002962  0.000000 0.000000 0.585899 0.585899      True
2025-01-01 2025-06-30  0.554530  0.569516 0.014987  1.000000 1.000000 0.613027 0.613027      True
```