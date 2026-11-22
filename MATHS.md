# Portimao maths

How Portimao works out its haem numbers, written so that the maths can be checked without reading the code. Each quantity has its equation, what every letter in it is (with its unit), a worked example in numbers, and the test that checks it. The numbers of each example are the numbers of its test, so the example and the program cannot drift apart: the tests are in the `tests/` folder of the development copy and are run each time the program is changed.

Two words used throughout:

- **Spectrum:** one reading of the spectrometer, taken about twice a second. Every quantity below is worked out for each spectrum, so each is a line against time.
- **Median:** the middle value when the values are put in order (the mean of the two middle ones when their number is even). It is used in place of the mean because one spike does not move it: the median of 11, 12, 30 is 12, while their mean is 17.7.

---

## 1. D, a haem's value

D is how large a haem's peak is in one spectrum, in mOD. It is worked out in four steps.

### 1.1 The attenuation of the spectrum

```text
A = −log10(T)
```

- A: the attenuation at one wavelength (OD)
- T: the light that came through the sample, divided by the light of the reference, at that wavelength (a fraction, 1 for the same light as the reference)

Example: T = 0.1 (a tenth of the light) gives A = 1 OD; T = 0.01 gives A = 2 OD; T = 0.5 gives A = 0.301 OD.

Checked by: `test_attenuation_from_known_ratios` in `tests/test_processing_maths.py`.

### 1.2 The amount of each haem

Each spectrum is described, at every wavelength, as so much of each haem's shape on top of a smooth background:

```text
A = c1 × S1 + c2 × S2 + ... + background
```

- A: the attenuation measured at one wavelength (OD), from 1.1
- S1, S2, ...: the shape of each haem at that wavelength, from the fit file (OD per mM per cm, oxidised minus reduced)
- c1, c2, ...: the amount of each haem (mM for a 1 cm light path). These are the numbers the program finds
- background: the smooth attenuation under the haem peaks at that wavelength (OD), from 1.3. It holds two or three numbers of its own, which the program finds at the same time

The program finds the one set of numbers (the c, and those of the background) for which the right-hand side comes closest to the measured spectrum: the set that makes the sum, over all the wavelengths, of (measured A − right-hand side)² the smallest (least squares). Each spectrum is fitted by itself, in one step.

Notes:

- Only the wavelengths that every haem shape of the fit file covers are used.
- Where the spectrum has a wavelength between two wavelengths of the fit file, the shape is read off the straight line between them.
- The shapes are oxidised minus reduced, so an amount rises as its haem is oxidised and falls as it is reduced.

Example: a spectrum is built from five haem shapes in the amounts 0.0001, 0.0002, 0.0003, 0.0004 and 0.0005 mM, on a background of 0.4 OD plus a part that falls with wavelength, from 0.05 OD at the shortest wavelength to 0 at the longest. The program gives back those five amounts and that background, with nothing left over.

Checked by: `test_one_spectrum_gives_its_amounts_back` in `tests/test_haem_decomposition.py`.

### 1.3 The background (the scatter)

The sample is cloudy: the cells scatter light, which adds a smooth attenuation under the haem peaks, and it drifts during a run. The background of 1.2 stands for it. One of five backgrounds is chosen for the whole dataset, by the name the program shows:

```text
Rowan scatter:                         background = b0 + b1 × w + b2 × (w − w_mid)²
Valencia:                              background = b0 + b1 ÷ w²
Flat + 1/wavelength:                   background = b0 + b1 ÷ w
Flat + 1/wavelength + 1/wavelength²:   background = b0 + b1 ÷ w + b2 ÷ w²
Straight line:                         background = b0 + b1 × w
```

- background: the attenuation that is not haem, at one wavelength (OD)
- w: the wavelength (nm)
- w_mid: the wavelength halfway between the shortest and the longest wavelength used (nm)
- b0: the flat part, the same at every wavelength (OD)
- b1, b2: the size of each other part (a slope, a curve, or a part that falls as the wavelength rises). The program finds b0, b1 and b2 together with the haem amounts of 1.2; they are not used afterwards

Notes:

- Rowan scatter is the standard one. It is the background of the lab's own chamber scripts, part for part: a flat level, a straight slope, and a curve around the middle wavelength, so it can bend.
- Valencia is the background drawn in the instrument's own fit file, which follows 1 ÷ w² exactly.
- b0, b1 and b2 are found again for every spectrum, so the background can change through the run. They may come out positive or negative.
- The haem amounts depend on the background chosen, because the two are fitted together: what one background cannot follow is shared between the haems and what is left over.
- A measured background that is not of the chosen form cannot be followed exactly: something is then left over (measured A − right-hand side of 1.2).
- Inside the program each part other than the flat one is stretched to run from 0 to 1 over the wavelengths used. This changes the size of b1 and b2 only: the background fitted, and the haem amounts, are the same as with the equations above.

Example: the wavelength is written in hundreds of nm, x = w ÷ 100, so 550 nm is x = 5.5. A spectrum is built from five haem shapes in the amounts 0.0001 to 0.0005 mM of 1.2, on this background:

```text
background = 0.4 + 0.05 × (x − 5.5) + 0.05 × (x − 6)²
```

- at 500 nm (x = 5): 0.4 + 0.05 × (−0.5) + 0.05 × 1 = 0.4 − 0.025 + 0.05 = 0.425 OD
- at 550 nm (x = 5.5): 0.4 + 0 + 0.05 × 0.25 = 0.4125 OD
- at 600 nm (x = 6): 0.4 + 0.05 × 0.5 + 0 = 0.425 OD

It is a flat part, a slope and a curve, so Rowan scatter can follow it: the program gives back the five amounts and this background, with nothing left over. The same is done for each of the other four backgrounds, each with a flat part of 0.4 OD and 0.05 of each of its other parts (for Valencia, 0.4 + 0.05 ÷ x²: 0.4 + 0.05 ÷ 25 = 0.402 OD at 500 nm).

A second spectrum has the same haems on the Valencia background, 0.4 + 0.05 ÷ x², and is fitted with Rowan scatter, which cannot follow it exactly. The lines of the lab's chamber scripts, copied into the test, and the program give the same five amounts and the same leftover.

Checked by: `test_each_background_gives_back_the_amounts`, `test_rowan_scatter_is_the_chamber_scripts_background` and `test_the_background_answered_is_the_one_used` in `tests/test_haem_decomposition.py`.

### 1.4 From the amount to D

```text
D = c × h × 1000
```

- D: the haem's value in this spectrum (mOD)
- c: the amount of the haem in this spectrum (mM for a 1 cm light path), from 1.2
- h: the height of the haem's shape at its highest point, within the wavelengths used (OD per mM per cm)
- 1000: turns OD into mOD

D does not depend on how tall the shape is drawn in the fit file: a shape drawn twice as tall gives half the amount and the same D.

Example: c = 0.0001 mM and h = 10 OD per mM per cm give D = 0.0001 × 10 × 1000 = 1 mOD. A run of four spectra holding 1, 4, 3 and 2 times that amount gives D = 1, 4, 3 and 2 mOD.

Checked by: `test_a_series_gives_its_amounts_back` in `tests/test_haem_decomposition.py`.

---

## 2. ΔD, the change from the start

```text
ΔD = D − D_start
```

- ΔD: the change of the haem from where it starts (mOD)
- D: the haem's value in this spectrum (mOD), from 1
- D_start: the median of D over the haem's first 50 spectra after the ignored start (mOD)

Notes:

- The ignored start is the stretch at the start of the run that the user marks as ignored (5 min unless it is changed). 50 spectra are 25 s when a spectrum is taken every 0.5 s.
- Each haem has its own D_start.
- A spectrum without a value is skipped and the next one is counted in its place.
- Only one number is taken off the whole line, so the line keeps its shape: ΔD is 0 where the haem starts, negative where it is more reduced than at the start and positive where it is more oxidised.
- With fewer than 50 spectra left after the ignored parts, no ΔD is worked out and the program says so.
- Fitting the change of each spectrum from the first one, in place of the spectra themselves, gives the same ΔD: the fit is done in one step, so taking a spectrum off before the fit is the same as taking its amounts off after it.

Example (with 3 spectra in place of 50, so that it can be followed by hand): D is 12, 30, 11, 9.5, 4, 5, 20, 20 mOD. The first three are 12, 30, 11; in order 11, 12, 30, so D_start = 12 mOD. ΔD is then 0, 18, −1, −2.5, −8, −7, 8, 8 mOD: the fourth spectrum, at 9.5 mOD, gives 9.5 − 12 = −2.5 mOD. The spike of 30 did not set the start, and nor did the higher stretch of 20 at the end.

Checked by: `test_delta_d_zero_is_where_the_haem_starts` and `test_the_change_from_the_first_spectrum` in `tests/test_haem_decomposition.py`.

---

## 3. A haem's level in a region

A file has two regions, each a stretch of time marked by the user: the oxidised region, where the haems are taken to be fully oxidised, and the reduced region, where they are taken to be fully reduced. The program never places a region. One pair of regions serves every haem of the file; each haem has its own two levels.

```text
D_ox  = median of D over the spectra inside the oxidised region
D_red = median of D over the spectra inside the reduced region
```

- D_ox: the haem's fully oxidised level (mOD)
- D_red: the haem's fully reduced level (mOD)
- D: the haem's value in each spectrum (mOD), from 1
- inside: from the time the region starts to the time it ends, the spectra at both edges counted

Notes:

- A spectrum without a value for a haem is left out for that haem.
- A level needs at least 10 spectra with a value (5 s). With fewer, no level is worked out and the program says so.

Example (with a least number of 3 in place of 10): ten spectra, one a minute from 0 to 9 min, with D = 12, 13, 11, 12, 30, 10, 4, 5, 3, 4 mOD.

- Oxidised region, 0 to 4 min: 12, 13, 11, 12, 30; in order 11, 12, 12, 13, 30, so D_ox = 12 mOD.
- Reduced region, 6 to 9 min: 4, 5, 3, 4; in order 3, 4, 4, 5, so D_red = (4 + 4) ÷ 2 = 4 mOD.

Checked by: `test_a_level_is_the_median_in_the_region` and `test_the_least_spectra_of_the_program` in `tests/test_redox_regions.py`.

---

## 4. % oxidised

```text
P = (D − D_red) ÷ (D_ox − D_red) × 100
```

- P: how oxidised the haem is in this spectrum (%)
- D: the haem's value in this spectrum (mOD), from 1
- D_ox: the haem's fully oxidised level (mOD), from 3
- D_red: the haem's fully reduced level (mOD), from 3

Notes:

- P is 100 % at the oxidised level and 0 % at the reduced level.
- Values above 100 % and below 0 % are kept as they are, not cut off.
- A haem whose two levels are equal has no scale, so its % is left empty.
- ΔD in place of D gives the same P, as long as the two levels are taken from the same line: the number taken off cancels out.

Example: D_ox = 12, D_red = 4 and D = 10 mOD give P = (10 − 4) ÷ (12 − 4) × 100 = 6 ÷ 8 × 100 = 75 %. For the ten spectra of 3, P = (D − 4) ÷ 8 × 100:

| D (mOD) | 12 | 13 | 11 | 12 | 30 | 10 | 4 | 5 | 3 | 4 |
|---|---|---|---|---|---|---|---|---|---|---|
| P (%) | 100 | 112.5 | 87.5 | 100 | 325 | 75 | 0 | 12.5 | −12.5 | 0 |

Checked by: `test_percent_oxidised_runs_between_the_two_levels` in `tests/test_redox_regions.py`.

### 4.1 Which files are shown in % oxidised

The regions are optional, and each file has its own. A file has a % oxidised only when it has both regions:

- both the oxidised and the reduced region were marked on it;
- each still holds at least 10 spectra inside the used part of the run (not trimmed, not ignored). A region that reaches into a trimmed or ignored part is cut back to the used part first.

For such a file the program keeps D_ox and D_red of every haem, and P for every spectrum.

What happens otherwise:

- A file with no regions, or with only one, has no levels and no P. Nothing is guessed for it: when % oxidised is chosen for the plots, that file is drawn as ΔD, as its axis says, and the files with both regions are drawn in %.
- With no file having both regions, % oxidised is not offered at all.
- A figure that averages files together (the haem and OCR response) offers % oxidised only when every file in it has both regions, so a % is never averaged with a ΔD.

Example: a run is trimmed 2 min from its start. Its regions were marked at 2 to 8 min (oxidised) and 24 to 30 min (reduced) of the recording, which is 0 to 6 min and 22 to 28 min of the trimmed run. The haem is 12 mOD before 10 min, 10 mOD from 10 to 20 min and 4 mOD after: D_ox = 12 and D_red = 4, so P is 100 %, (10 − 4) ÷ 8 × 100 = 75 % and 0 %. The same run without its reduced region has no P and is shown as ΔD.

Checked by: `test_a_file_needs_both_regions_for_its_levels` in `tests/test_redox_regions.py` and `test_a_file_with_both_regions_gets_percent_oxidised` in `tests/test_processing_maths.py`.

---

## 5. An edge copied to another file

The runs of a dataset are taken to be done in the same way, so an edge of a region set on one file can be copied to the others. It is copied by the addition nearest to it, not by its time: an edge 1.5 min before the third addition is put 1.5 min before the third addition of every other file.

```text
d = t − a
t_new = a_new + d
```

- t: the time of the edge in the file it was set on (min)
- a: the time of the addition nearest to the edge in that file (min)
- d: the distance of the edge from that addition (min); negative before the addition, positive after it
- a_new: the time of the addition of the same number in the other file (min)
- t_new: the time of the edge in the other file (min)

Notes:

- The additions are counted in order of time (first, second, third, ...), not matched by their labels, which may have typing mistakes.
- Halfway between two additions, the earlier one is taken.
- An edge before the first addition is copied by its distance to the first addition.
- A file that has no addition of that number (it has fewer additions) is not given the edge: it keeps the region it had.

Example: one file has its additions at 5, 12, 20 and 30 min, another at 6, 13, 22 and 31 min. An edge at t = 18.5 min in the first file is 13.5, 6.5, 1.5 and 11.5 min from its four additions, so the third is nearest: a = 20 and d = 18.5 − 20 = −1.5 min. In the other file the third addition is at a_new = 22 min, so t_new = 22 − 1.5 = 20.5 min. A file with only two additions is not given this edge.

Checked by: `test_an_edge_is_copied_by_its_nearest_addition` in `tests/test_redox_regions.py`.

---

## 6. Δψ, the membrane potential, from bH and bL

The two b haems sit at different depths in the membrane, so the membrane potential pushes electrons from one to the other: the higher Δψ, the more reduced bL is next to bH. Δψ is worked out from how reduced the two are in each spectrum. The method is that of Kim, Ripple and Springett, "Measurement of the mitochondrial membrane potential and pH gradient from the redox poise of the hemes of the bc1 complex", Biophysical Journal 2012, 102:1194 to 1203 (doi 10.1016/j.bpj.2012.02.003), section "Equilibrium measurement of membrane potential".

Step 1, how reduced each haem is, as a fraction:

```text
R_H = 1 − P_H ÷ 100
R_L = 1 − P_L ÷ 100
```

Step 2, the four states of the pair of haems. A pair has neither haem reduced, only bH, only bL, or both:

```text
R_H = h + b
R_L = l + b
n + h + l + b = 1
```

Step 3, an electron on one haem pushes a second one away, which makes "both reduced" rarer by a fixed factor:

```text
(b × n) ÷ (h × l) = k
k = e^(−(M_H1 − M_H2) ÷ s)
s = R × T ÷ F
```

Steps 2 and 3 together give b (below), and then h = R_H − b, l = R_L − b and n = 1 − R_H − R_L + b.

Step 4, the redox potential at each haem:

```text
E_H = M_H1 − s × ln(h ÷ n)
E_L = M_L1 − s × ln(l ÷ n)
```

Step 5, the membrane potential:

```text
Δψ = (E_H − E_L) ÷ β
```

- P_H, P_L: how oxidised bH and bL are in this spectrum (%), from 4
- R_H, R_L: the fraction of bH and of bL that is reduced (0 to 1)
- n, h, l, b: the fractions of the pairs with neither haem reduced, only bH reduced, only bL reduced, and both reduced (0 to 1)
- M_H1, M_L1: the midpoint potential of bH and of bL while the other haem is oxidised (mV); +40 and −20
- M_H2, M_L2: the midpoint potential of bH and of bL while the other haem is reduced (mV); −30 and −90
- k: how much rarer "both reduced" is made by the push (no unit); 0.0729 at 37 °C, as M_H1 − M_H2 = 70 mV
- s: the voltage that goes with the temperature (mV); 26.727 at 37 °C
- R: the gas constant, 8.314462618 J/mol/K
- T: the temperature of the sample (K), its temperature in °C + 273.15; 37 °C unless changed
- F: the Faraday constant, 96485.33212 C/mol
- E_H, E_L: the redox potential at bH and at bL (mV)
- β: the share of the membrane potential that lies between the two haems (no unit); 0.5, half
- Δψ: the membrane potential (mV)

How b is found: putting step 2 into step 3 leaves one equation with b alone,

```text
(1 − k) × b² + B × b − k × R_H × R_L = 0
B = 1 − (1 − k) × (R_H + R_L)
b = 2 × k × R_H × R_L ÷ (B + √(B² + 4 × (1 − k) × k × R_H × R_L))
```

which has only this one answer between 0 and the smaller of R_H and R_L.

Notes:

- The midpoint potentials, β and the temperature above are the paper's, measured on the bc1 complex of mitochondria. They are the numbers the program starts with; each is kept with the dataset so that it can be changed for another organism.
- M_H1 − M_H2 must equal M_L1 − M_L2 (70 mV for both here): each is the push of one electron on the other. Numbers that break this are refused.
- Δψ is left empty in a spectrum where bH or bL is less than 10 % or more than 90 % reduced (the paper's rule): outside these limits a small error in the % gives a large error in Δψ. A haem exactly at a limit is kept.
- The paper finds E_H and β × Δψ by fitting a model to R_H and R_L. With two measured values and two unknowns nothing is left over to fit, so the equations above give the same two numbers directly.
- Only a file with both regions has P, so only such a file has Δψ; its fit must have one bH and one bL.
- The program keeps E_H and E_L beside Δψ for every spectrum.

Example 1: bH and bL are both 65.0858 % oxidised at 37 °C, so R_H = R_L = 0.349142. Then b = 0.023713, h = l = 0.349142 − 0.023713 = 0.325429 and n = 1 − 0.698284 + 0.023713 = 0.325429 (check: b × n ÷ (h × l) = 0.023713 ÷ 0.325429 = 0.0729 = k). E_H = 40 − 26.727 × ln(1) = 40 mV and E_L = −20 − 26.727 × ln(1) = −20 mV, so Δψ = (40 + 20) ÷ 0.5 = 120 mV.

Example 2: bH is 75.6308 % and bL 40.6805 % oxidised at 37 °C, so R_H = 0.243692 and R_L = 0.593195. Then b = 0.040289, h = 0.203403, l = 0.552906 and n = 0.203403. E_H = 40 − 26.727 × ln(0.203403 ÷ 0.203403) = 40 mV and E_L = −20 − 26.727 × ln(0.552906 ÷ 0.203403) = −20 − 26.727 × 1 = −46.727 mV, so Δψ = (40 + 46.727) ÷ 0.5 = 173.453 mV.

Checked by: `test_equal_haems_at_their_midpoints_give_120_mV`, `test_unequal_haems_give_173_mV`, `test_delta_psi_is_empty_outside_the_limits`, `test_numbers_that_cannot_be_used_are_refused` and `test_the_numbers_the_program_starts_with` in `tests/test_delta_psi.py`.
