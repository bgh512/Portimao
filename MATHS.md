# Portimao maths

How Portimao works out its haem numbers (and, in section 8, the concentration of each addition; in section 9, the difference spectrum, its haem bands and the waterfall; in section 10, the traces over time lined up on their additions and averaged; in section 11, the numbers per region of a dataset figure and their statistics), written so that the maths can be checked without reading the code. Each quantity has its equation, what every letter in it is (with its unit), a worked example in numbers, and the test that checks it. The numbers of each example are the numbers of its test, so the example and the program cannot drift apart: the tests are in the `tests/` folder of the development copy and are run each time the program is changed.

The equations are written as a textbook writes them, which GitHub and VS Code's preview show typeset.

Two words used throughout:

- **Spectrum:** one reading of the spectrometer, taken about twice a second. Every quantity below is worked out for each spectrum, so each is a line against time.
- **Median:** the middle value when the values are put in order (the mean of the two middle ones when their number is even). It is used in place of the mean because one spike does not move it: the median of 11, 12, 30 is 12, while their mean is 17.7.

---

## 1. D, a haem's value

$D$ is how large a haem's peak is in one spectrum, in mOD. It is worked out in four steps.

### 1.1 The attenuation of the spectrum

$$A = -\log_{10} T$$

- $A$: the attenuation at one wavelength (OD)
- $T$: the light that came through the sample, divided by the light of the reference, at that wavelength (a fraction, 1 for the same light as the reference)

Example: $T = 0.1$ (a tenth of the light) gives $A = 1$ OD; $T = 0.01$ gives $A = 2$ OD; $T = 0.5$ gives $A = 0.301$ OD.

Checked by: `test_attenuation_from_known_ratios` in `tests/test_processing_maths.py`.

### 1.2 The amount of each haem

Each spectrum is described, at every wavelength, as so much of each haem's shape on top of a smooth background:

$$A = c_1 S_1 + c_2 S_2 + \dots + B$$

- $A$: the attenuation measured at one wavelength (OD), from 1.1
- $S_1, S_2, \dots$: the shape of each haem at that wavelength, from the fit file (OD mM⁻¹ cm⁻¹, oxidised minus reduced)
- $c_1, c_2, \dots$: the amount of each haem (mM for a 1 cm light path). These are the numbers the program finds
- $B$: the background, the smooth attenuation under the haem peaks at that wavelength (OD), from 1.3. It holds two or three numbers of its own, which the program finds at the same time

The program finds the one set of numbers (the $c$, and those of the background) for which the right-hand side comes closest to the measured spectrum: the set that makes

$$\sum_{\text{wavelengths}} \bigl(A - (c_1 S_1 + c_2 S_2 + \dots + B)\bigr)^2$$

the smallest (least squares). Each spectrum is fitted by itself, in one step.

Notes:

- Only the wavelengths that every haem shape of the fit file covers are used.
- Where the spectrum has a wavelength between two wavelengths of the fit file, the shape is read off the straight line between them.
- The shapes are oxidised minus reduced, so an amount rises as its haem is oxidised and falls as it is reduced.

Example: a spectrum is built from five haem shapes in the amounts 0.0001, 0.0002, 0.0003, 0.0004 and 0.0005 mM, on a background of 0.4 OD plus a part that falls with wavelength, from 0.05 OD at the shortest wavelength to 0 at the longest. The program gives back those five amounts and that background, with nothing left over.

Checked by: `test_one_spectrum_gives_its_amounts_back` in `tests/test_haem_decomposition.py`.

### 1.3 The background (the scatter)

The sample is cloudy: the cells scatter light, which adds a smooth attenuation under the haem peaks, and it drifts during a run. The background $B$ of 1.2 stands for it. One of five backgrounds is chosen for the whole dataset, by the name the program shows (the ⓘ button beside Scatter shows the same formula):

Rowan scatter:

$$B = b_0 + b_1\,w + b_2\,(w - w_{\mathrm{mid}})^2$$

Palencia:

$$B = b_0 + \frac{b_1}{w^2}$$

Inverse:

$$B = b_0 + \frac{b_1}{w}$$

Inverse²:

$$B = b_0 + \frac{b_1}{w} + \frac{b_2}{w^2}$$

Linear:

$$B = b_0 + b_1\,w$$

- $B$: the background, the attenuation that is not haem, at one wavelength (OD)
- $w$: the wavelength (nm)
- $w_{\mathrm{mid}}$: the wavelength halfway between the shortest and the longest wavelength used (nm)
- $b_0$: the flat part, the same at every wavelength (OD)
- $b_1$, $b_2$: the size of each other part (a slope, a curve, or a part that falls as the wavelength rises). The program finds $b_0$, $b_1$ and $b_2$ together with the haem amounts of 1.2; they are not used afterwards

Notes:

- Rowan scatter is the standard one. It is the background of the lab's own chamber scripts, part for part: a flat level, a straight slope, and a curve around the middle wavelength, so it can bend.
- Palencia (called Valencia before November 2026) is the background drawn in the instrument's own fit file, which follows $\dfrac{1}{w^2}$ exactly.
- Linear and Inverse differ only a little over the wavelengths the fit uses (about 500 to 630 nm): $\dfrac{1}{w}$ bends slightly, and strays from a straight line by at most about 6 % of its change, in the middle.
- $b_0$, $b_1$ and $b_2$ are found again for every spectrum, so the background can change through the run. They may come out positive or negative.
- The haem amounts depend on the background chosen, because the two are fitted together: what one background cannot follow is shared between the haems and what is left over.
- A measured background that is not of the chosen form cannot be followed exactly: something is then left over (measured $A$ minus the right-hand side of 1.2).
- Inside the program each part other than the flat one is stretched to run from 0 to 1 over the wavelengths used. This changes the size of $b_1$ and $b_2$ only: the background fitted, and the haem amounts, are the same as with the equations above.

Example: the wavelength is written in hundreds of nm, $x = \dfrac{w}{100}$, so 550 nm is $x = 5.5$. A spectrum is built from five haem shapes in the amounts 0.0001 to 0.0005 mM of 1.2, on this background:

$$B = 0.4 + 0.05\,(x - 5.5) + 0.05\,(x - 6)^2$$

- at 500 nm ($x = 5$): $B = 0.4 + 0.05 \times (-0.5) + 0.05 \times 1 = 0.4 - 0.025 + 0.05 = 0.425$ OD
- at 550 nm ($x = 5.5$): $B = 0.4 + 0 + 0.05 \times 0.25 = 0.4125$ OD
- at 600 nm ($x = 6$): $B = 0.4 + 0.05 \times 0.5 + 0 = 0.425$ OD

It is a flat part, a slope and a curve, so Rowan scatter can follow it: the program gives back the five amounts and this background, with nothing left over. The same is done for each of the other four backgrounds, each with a flat part of 0.4 OD and 0.05 of each of its other parts. For Palencia at 500 nm:

$$B = 0.4 + \frac{0.05}{x^2} = 0.4 + \frac{0.05}{25} = 0.402 \text{ OD}$$

A second spectrum has the same haems on the Palencia background, $B = 0.4 + \dfrac{0.05}{x^2}$, and is fitted with Rowan scatter, which cannot follow it exactly. The lines of the lab's chamber scripts, copied into the test, and the program give the same five amounts and the same leftover.

Checked by: `test_each_background_gives_back_the_amounts`, `test_rowan_scatter_is_the_chamber_scripts_background` and `test_the_background_answered_is_the_one_used` in `tests/test_haem_decomposition.py`.

### 1.4 From the amount to D

$$D = 1000\,c\,h$$

- $D$: the haem's value in this spectrum (mOD)
- $c$: the amount of the haem in this spectrum (mM for a 1 cm light path), from 1.2
- $h$: the height of the haem's shape at its highest point, within the wavelengths used (OD mM⁻¹ cm⁻¹)
- 1000: turns OD into mOD

$D$ does not depend on how tall the shape is drawn in the fit file: a shape drawn twice as tall gives half the amount and the same $D$.

Example: $c = 0.0001$ mM and $h = 10$ OD mM⁻¹ cm⁻¹ give $D = 1000 \times 0.0001 \times 10 = 1$ mOD. A run of four spectra holding 1, 4, 3 and 2 times that amount gives $D$ = 1, 4, 3 and 2 mOD.

Checked by: `test_a_series_gives_its_amounts_back` in `tests/test_haem_decomposition.py`.

---

## 2. ΔD, the change from the start

$$\Delta D = D - D_{\mathrm{start}}$$

- $\Delta D$: the change of the haem from where it starts (mOD)
- $D$: the haem's value in this spectrum (mOD), from 1
- $D_{\mathrm{start}}$: the median of $D$ over the haem's first 50 spectra after the ignored start (mOD)

Notes:

- The ignored start is the stretch at the start of the run that the user marks as ignored (5 min unless it is changed). 50 spectra are 25 s when a spectrum is taken every 0.5 s.
- Each haem has its own $D_{\mathrm{start}}$.
- A spectrum without a value is skipped and the next one is counted in its place.
- Only one number is taken off the whole line, so the line keeps its shape: $\Delta D$ is 0 where the haem starts, negative where it is more reduced than at the start and positive where it is more oxidised.
- With fewer than 50 spectra left after the ignored parts, no $\Delta D$ is worked out and the program says so.
- Fitting the change of each spectrum from the first one, in place of the spectra themselves, gives the same $\Delta D$: the fit is done in one step, so taking a spectrum off before the fit is the same as taking its amounts off after it.

Example (with 3 spectra in place of 50, so that it can be followed by hand): $D$ is 12, 30, 11, 9.5, 4, 5, 20, 20 mOD. The first three are 12, 30, 11; in order 11, 12, 30, so $D_{\mathrm{start}} = 12$ mOD. $\Delta D$ is then 0, 18, −1, −2.5, −8, −7, 8, 8 mOD: the fourth spectrum, at 9.5 mOD, gives $\Delta D = 9.5 - 12 = -2.5$ mOD. The spike of 30 did not set the start, and nor did the higher stretch of 20 at the end.

Checked by: `test_delta_d_zero_is_where_the_haem_starts` and `test_the_change_from_the_first_spectrum` in `tests/test_haem_decomposition.py`.

---

## 3. A haem's level in a region

A file has two regions, each a stretch of time marked by the user: the oxidised region, where the haems are taken to be fully oxidised, and the reduced region, where they are taken to be fully reduced. The program never places a region. One pair of regions serves every haem of the file; each haem has its own two levels.

$$D_{\mathrm{ox}} = \operatorname{median}(D \text{ inside the oxidised region})$$

$$D_{\mathrm{red}} = \operatorname{median}(D \text{ inside the reduced region})$$

- $D_{\mathrm{ox}}$: the haem's fully oxidised level (mOD)
- $D_{\mathrm{red}}$: the haem's fully reduced level (mOD)
- $D$: the haem's value in each spectrum (mOD), from 1
- inside: from the time the region starts to the time it ends, the spectra at both edges counted

Notes:

- A spectrum without a value for a haem is left out for that haem.
- A level needs at least 10 spectra with a value (5 s). With fewer, no level is worked out and the program says so.

Example (with a least number of 3 in place of 10): ten spectra, one a minute from 0 to 9 min, with $D$ = 12, 13, 11, 12, 30, 10, 4, 5, 3, 4 mOD.

- Oxidised region, 0 to 4 min: 12, 13, 11, 12, 30; in order 11, 12, 12, 13, 30, so $D_{\mathrm{ox}} = 12$ mOD.
- Reduced region, 6 to 9 min: 4, 5, 3, 4; in order 3, 4, 4, 5, so $D_{\mathrm{red}} = \dfrac{4 + 4}{2} = 4$ mOD.

Checked by: `test_a_level_is_the_median_in_the_region` and `test_the_least_spectra_of_the_program` in `tests/test_redox_regions.py`.

---

## 4. % oxidised

$$P = \frac{D - D_{\mathrm{red}}}{D_{\mathrm{ox}} - D_{\mathrm{red}}} \times 100$$

- $P$: how oxidised the haem is in this spectrum (%)
- $D$: the haem's value in this spectrum (mOD), from 1
- $D_{\mathrm{ox}}$: the haem's fully oxidised level (mOD), from 3
- $D_{\mathrm{red}}$: the haem's fully reduced level (mOD), from 3

Notes:

- $P$ is 100 % at the oxidised level and 0 % at the reduced level.
- Values above 100 % and below 0 % are kept as they are, not cut off.
- A haem whose two levels are equal has no scale, so its % is left empty.
- $\Delta D$ in place of $D$ gives the same $P$, as long as the two levels are taken from the same line: the number taken off cancels out.

Example: $D_{\mathrm{ox}} = 12$, $D_{\mathrm{red}} = 4$ and $D = 10$ mOD give

$$P = \frac{10 - 4}{12 - 4} \times 100 = \frac{6}{8} \times 100 = 75\ \%$$

For the ten spectra of 3, $P = \dfrac{D - 4}{8} \times 100$:

| D (mOD) | 12 | 13 | 11 | 12 | 30 | 10 | 4 | 5 | 3 | 4 |
|---|---|---|---|---|---|---|---|---|---|---|
| P (%) | 100 | 112.5 | 87.5 | 100 | 325 | 75 | 0 | 12.5 | −12.5 | 0 |

Checked by: `test_percent_oxidised_runs_between_the_two_levels` in `tests/test_redox_regions.py`.

### 4.1 Which files are shown in % oxidised

The regions are optional, and each file has its own. A file has a % oxidised only when it has both regions:

- both the oxidised and the reduced region were marked on it;
- each still holds at least 10 spectra inside the used part of the run (not trimmed, not ignored). A region that reaches into a trimmed or ignored part is cut back to the used part first.

For such a file the program keeps $D_{\mathrm{ox}}$ and $D_{\mathrm{red}}$ of every haem, and $P$ for every spectrum.

What happens otherwise:

- A file with no regions, or with only one, has no levels and no $P$. Nothing is guessed for it: when % oxidised is chosen for the plots, that file is drawn as $\Delta D$, as its axis says, and the files with both regions are drawn in %.
- With no file having both regions, % oxidised is not offered at all.
- A figure that averages files together (the haem and OCR response) offers % oxidised only when every file in it has both regions, so a % is never averaged with a $\Delta D$.

Example: a run is trimmed 2 min from its start. Its regions were marked at 2 to 8 min (oxidised) and 24 to 30 min (reduced) of the recording, which is 0 to 6 min and 22 to 28 min of the trimmed run. The haem is 12 mOD before 10 min, 10 mOD from 10 to 20 min and 4 mOD after: $D_{\mathrm{ox}} = 12$ and $D_{\mathrm{red}} = 4$, so $P$ is 100 %, $\dfrac{10 - 4}{8} \times 100 = 75$ % and 0 %. The same run without its reduced region has no $P$ and is shown as $\Delta D$.

Checked by: `test_a_file_needs_both_regions_for_its_levels` in `tests/test_redox_regions.py` and `test_a_file_with_both_regions_gets_percent_oxidised` in `tests/test_processing_maths.py`.

---

## 5. An edge copied to another file

The runs of a dataset are taken to be done in the same way, so an edge of a region set on one file can be copied to the others. It is copied by the addition nearest to it, not by its time: an edge 1.5 min before the third addition is put 1.5 min before the third addition of every other file.

$$d = t - a$$

$$t_{\mathrm{new}} = a_{\mathrm{new}} + d$$

- $t$: the time of the edge in the file it was set on (min)
- $a$: the time of the addition nearest to the edge in that file (min)
- $d$: the distance of the edge from that addition (min); negative before the addition, positive after it
- $a_{\mathrm{new}}$: the time of the addition of the same number in the other file (min)
- $t_{\mathrm{new}}$: the time of the edge in the other file (min)

Notes:

- The additions are counted in order of time (first, second, third, ...), not matched by their labels, which may have typing mistakes.
- Halfway between two additions, the earlier one is taken.
- An edge before the first addition is copied by its distance to the first addition.
- A file that has no addition of that number (it has fewer additions) is not given the edge: it keeps the region it had.

Example: one file has its additions at 5, 12, 20 and 30 min, another at 6, 13, 22 and 31 min. An edge at $t = 18.5$ min in the first file is 13.5, 6.5, 1.5 and 11.5 min from its four additions, so the third is nearest: $a = 20$ and $d = 18.5 - 20 = -1.5$ min. In the other file the third addition is at $a_{\mathrm{new}} = 22$ min, so $t_{\mathrm{new}} = 22 - 1.5 = 20.5$ min. A file with only two additions is not given this edge.

An edge after the last addition is copied by its distance from the end instead, so a region that runs to the end of one file runs to the end of every file, whatever the number of additions:

$$e = E - t$$

$$t_{\mathrm{new}} = E_{\mathrm{new}} - e$$

- $E$: the end of the used part of the file the edge was set on (min): the end of the plot, less any ignored end
- $e$: the distance of the edge from that end (min)
- $E_{\mathrm{new}}$: the end of the used part of the other file (min)

Example: a file has its additions at 10, 15 and 20 min and its used part ends at $E = 30$ min; another has its additions at 11, 16 and 22 min and ends at $E_{\mathrm{new}} = 34$ min; a third has only two additions, at 9 and 14 min, and ends at 26 min. An edge at $t = 29$ min in the first file is after its last addition, so $e = 30 - 29 = 1$ min, and $t_{\mathrm{new}} = 34 - 1 = 33$ min in the second file and $26 - 1 = 25$ min in the third, which has fewer additions but is still given the edge.

Checked by: `test_an_edge_is_copied_by_its_nearest_addition` and `test_an_edge_after_the_last_addition_is_copied_from_the_end` in `tests/test_redox_regions.py`.

---

## 6. Δψ, the membrane potential, from bH and bL

The two b haems sit at different depths in the membrane, so the membrane potential pushes electrons from one to the other: the higher $\Delta\psi$, the more reduced bL is next to bH. $\Delta\psi$ is worked out from how reduced the two are in each spectrum. The method is that of Kim, Ripple and Springett, "Measurement of the mitochondrial membrane potential and pH gradient from the redox poise of the hemes of the bc1 complex", Biophysical Journal 2012, 102:1194 to 1203 (doi 10.1016/j.bpj.2012.02.003), section "Equilibrium measurement of membrane potential".

Step 1, how reduced each haem is, as a fraction:

$$R_{\mathrm{H}} = 1 - \frac{P_{\mathrm{H}}}{100} \qquad R_{\mathrm{L}} = 1 - \frac{P_{\mathrm{L}}}{100}$$

Step 2, the four states of the pair of haems. A pair has neither haem reduced, only bH, only bL, or both:

$$R_{\mathrm{H}} = h + b \qquad R_{\mathrm{L}} = l + b \qquad n + h + l + b = 1$$

Step 3, an electron on one haem pushes a second one away, which makes "both reduced" rarer by a fixed factor:

$$\frac{b\,n}{h\,l} = k \qquad k = e^{-(M_{\mathrm{H1}} - M_{\mathrm{H2}})/s} \qquad s = \frac{RT}{F}$$

Steps 2 and 3 together give $b$ (below), and then $h = R_{\mathrm{H}} - b$, $l = R_{\mathrm{L}} - b$ and $n = 1 - R_{\mathrm{H}} - R_{\mathrm{L}} + b$.

Step 4, the redox potential at each haem:

$$E_{\mathrm{H}} = M_{\mathrm{H1}} - s \ln\frac{h}{n} \qquad E_{\mathrm{L}} = M_{\mathrm{L1}} - s \ln\frac{l}{n}$$

Step 5, the membrane potential:

$$\Delta\psi = \frac{E_{\mathrm{H}} - E_{\mathrm{L}}}{\beta}$$

- $P_{\mathrm{H}}$, $P_{\mathrm{L}}$: how oxidised bH and bL are in this spectrum (%), from 4
- $R_{\mathrm{H}}$, $R_{\mathrm{L}}$: the fraction of bH and of bL that is reduced (0 to 1)
- $n$, $h$, $l$, $b$: the fractions of the pairs with neither haem reduced, only bH reduced, only bL reduced, and both reduced (0 to 1)
- $M_{\mathrm{H1}}$, $M_{\mathrm{L1}}$: the midpoint potential of bH and of bL while the other haem is oxidised (mV); +40 and −20
- $M_{\mathrm{H2}}$, $M_{\mathrm{L2}}$: the midpoint potential of bH and of bL while the other haem is reduced (mV); −30 and −90
- $k$: how much rarer "both reduced" is made by the push (no unit); 0.0729 at 37 °C, as $M_{\mathrm{H1}} - M_{\mathrm{H2}} = 70$ mV
- $s$: the voltage that goes with the temperature (mV); 26.727 at 37 °C
- $R$: the gas constant, 8.314462618 J mol⁻¹ K⁻¹
- $T$: the temperature of the sample (K), its temperature in °C + 273.15; 37 °C unless changed
- $F$: the Faraday constant, 96485.33212 C mol⁻¹
- $E_{\mathrm{H}}$, $E_{\mathrm{L}}$: the redox potential at bH and at bL (mV)
- $\beta$: the share of the membrane potential that lies between the two haems (no unit); 0.5, half
- $\Delta\psi$: the membrane potential (mV)

How $b$ is found: putting step 2 into step 3 leaves one equation with $b$ alone,

$$(1 - k)\,b^2 + B\,b - k\,R_{\mathrm{H}} R_{\mathrm{L}} = 0$$

$$B = 1 - (1 - k)\,(R_{\mathrm{H}} + R_{\mathrm{L}})$$

$$b = \frac{2\,k\,R_{\mathrm{H}} R_{\mathrm{L}}}{B + \sqrt{B^2 + 4\,(1 - k)\,k\,R_{\mathrm{H}} R_{\mathrm{L}}}}$$

which has only this one answer between 0 and the smaller of $R_{\mathrm{H}}$ and $R_{\mathrm{L}}$. ($B$ here is a number of this section only, not the background of 1.3.)

Notes:

- The midpoint potentials, $\beta$ and the temperature above are the paper's, measured on the bc1 complex of mitochondria. They are the numbers the program starts with; each is kept with the dataset so that it can be changed for another organism, in the Δψ row of the strip under the plot.
- $M_{\mathrm{H1}} - M_{\mathrm{H2}}$ must equal $M_{\mathrm{L1}} - M_{\mathrm{L2}}$ (70 mV for both here): each is the push of one electron on the other. So the program has $M_{\mathrm{H1}}$, $M_{\mathrm{L1}}$ and this fall typed (the **shift** box of the Δψ box), and fills in $M_{\mathrm{H2}} = M_{\mathrm{H1}} - \text{fall}$ and $M_{\mathrm{L2}} = M_{\mathrm{L1}} - \text{fall}$ itself (40 and −20 with a fall of 70 give −30 and −90; with a fall of 60, −20 and −80). Numbers that break the rule cannot be typed, and are refused if they reach the maths another way.
- $\Delta\psi$ is left empty in a spectrum where bH or bL is less than 10 % or more than 90 % reduced (the paper's rule): outside these limits a small error in the % gives a large error in $\Delta\psi$. A haem exactly at a limit is kept. The two limits can be changed in the same row.
- The paper finds $E_{\mathrm{H}}$ and $\beta\,\Delta\psi$ by fitting a model to $R_{\mathrm{H}}$ and $R_{\mathrm{L}}$. With two measured values and two unknowns nothing is left over to fit, so the equations above give the same two numbers directly.
- Only a file with both regions has $P$, so only such a file has $\Delta\psi$; its fit must have one bH and one bL.
- The program keeps $E_{\mathrm{H}}$ and $E_{\mathrm{L}}$ beside $\Delta\psi$ for every spectrum.

Example 1: bH and bL are both 65.0858 % oxidised at 37 °C, so $R_{\mathrm{H}} = R_{\mathrm{L}} = 0.349142$. Then $b = 0.023713$, $h = l = 0.349142 - 0.023713 = 0.325429$ and $n = 1 - 0.698284 + 0.023713 = 0.325429$ (check: $\dfrac{b\,n}{h\,l} = \dfrac{0.023713}{0.325429} = 0.0729 = k$). Then

$$E_{\mathrm{H}} = 40 - 26.727 \ln 1 = 40 \text{ mV} \qquad E_{\mathrm{L}} = -20 - 26.727 \ln 1 = -20 \text{ mV}$$

$$\Delta\psi = \frac{40 + 20}{0.5} = 120 \text{ mV}$$

Example 2: bH is 75.6308 % and bL 40.6805 % oxidised at 37 °C, so $R_{\mathrm{H}} = 0.243692$ and $R_{\mathrm{L}} = 0.593195$. Then $b = 0.040289$, $h = 0.203403$, $l = 0.552906$ and $n = 0.203403$. Then

$$E_{\mathrm{H}} = 40 - 26.727 \ln\frac{0.203403}{0.203403} = 40 \text{ mV}$$

$$E_{\mathrm{L}} = -20 - 26.727 \ln\frac{0.552906}{0.203403} = -20 - 26.727 \times 1 = -46.727 \text{ mV}$$

$$\Delta\psi = \frac{40 + 46.727}{0.5} = 173.453 \text{ mV}$$

Checked by: `test_equal_haems_at_their_midpoints_give_120_mV`, `test_unequal_haems_give_173_mV`, `test_delta_psi_is_empty_outside_the_limits`, `test_numbers_that_cannot_be_used_are_refused` and `test_the_numbers_the_program_starts_with` in `tests/test_delta_psi.py`; the filled-in midpoints by `test_numbers_of_the_delta_psi_row` in `tests/test_window_parts.py`.

---

## 7. The averaging regions

An averaging region is a stretch of time over which a measurement (the OCR, a haem, a spectrum) is averaged. There are two kinds, and a dataset can have either or both:

- A **settled region** is the stretch before an addition, once the measurement has settled after the addition before. Every settled region has the same length, $w$, and ends the same time, $g$, before the next addition, in every file of the dataset, unless it is set on its own (7.5).
- A **quick region** is the stretch just after an addition, for the quick response to it. Every quick region has the same length, $q$, and starts the same time, $d$, after its own addition, in every file of the dataset, unless it is set on its own (7.5).

The region before the first addition is the baseline, which both kinds are compared with. Every figure that averages around the additions uses these regions; a figure that averages files together uses one kind, which it asks for when the dataset has both.

### 7.1 The baseline and the settled regions

The baseline, before the first addition:

$$\mathrm{end}_0 = a_1 - g \qquad \mathrm{start}_0 = \mathrm{end}_0 - w$$

The region after addition number $i$, when another addition follows:

$$\mathrm{end}_i = a_{i+1} - g \qquad \mathrm{start}_i = \mathrm{end}_i - w$$

The region after the last addition:

$$\mathrm{end}_{\mathrm{last}} = T - f \qquad \mathrm{start}_{\mathrm{last}} = \mathrm{end}_{\mathrm{last}} - w$$

- $a_1, a_2, \dots$: the times of the additions, in order (min); an addition marked to be ignored is left out
- $w$: the length of the baseline and of every settled region (min; typed in seconds in the program, 120 s to start with)
- $g$: the gap between the end of the baseline or of a settled region and the next addition (min; typed in seconds, 30 s to start with)
- $T$: the time of the last measurement of the file, after trimming (min)
- $f$: the gap between the last region and the end of the file (min; 0.5 min to start with, and set by moving the right edge of the last region)
- start, end: the first and last time of a region (min); the measurements from start to end, both included, are averaged

Notes:

- When the baseline would start before the file does, it starts where the file starts, so it is shorter than $w$. A baseline with less than 10 s of data is left out, and the file then has no baseline.
- A region that would start before its own addition ($\mathrm{start}_i$ before $a_i$) does not fit: the additions are too close together for a region of that length. It is left out and named in a warning, and is never shortened.
- The average of a region is the mean of its measurements, and the spread is their standard deviation (dividing by their number minus 1).
- The baseline is there whenever the dataset has averaging regions of either kind, with the length $w$ and the gap $g$, also when it has quick regions only.

Example 1: a file of 30 min with additions at 10 and 20 min, $w = 2$ min and $g = 0.5$ min. The baseline ends at $10 - 0.5 = 9.5$ min and starts at $9.5 - 2 = 7.5$ min. The region after the first addition ends at $20 - 0.5 = 19.5$ min and starts at 17.5 min. The region after the last addition ends at $30 - 0.5 = 29.5$ min and starts at 27.5 min.

Example 2: the same file with $w = 12$ min. The baseline would start at $9.5 - 12 = -2.5$ min, so it starts at 0 and runs to 9.5 min. The region after the first addition would start at $19.5 - 12 = 7.5$ min, before its addition at 10 min, and the last would start at $29.5 - 12 = 17.5$ min, before its addition at 20 min: neither fits, and both are left out.

Checked by: `test_the_windows_fall_before_the_additions` in `tests/test_averaging_windows.py`; the averages inside the regions by `test_averages_around_the_additions` and `test_average_that_does_not_fit` in `tests/test_processing_maths.py`; the averaged spectra of the time response by `test_averaged_spectra_around_the_additions` and `test_baseline_starts_with_the_recording` in `tests/test_summary_maths.py`.

### 7.2 The quick regions

The quick region after addition number $i$:

$$\mathrm{start}_i = a_i + d \qquad \mathrm{end}_i = \mathrm{start}_i + q$$

- $a_i$: the time of addition number $i$ (min)
- $d$: how long after its addition a quick region starts (min; typed in seconds in the program, 10 s to start with)
- $q$: the length of every quick region (min; typed in seconds, 30 s to start with)
- start, end: the first and last time of the region (min); the measurements from start to end, both included, are averaged

Notes:

- A quick region that would end after the next addition ($\mathrm{end}_i$ after $a_{i+1}$), or after the last measurement of the file for the last addition, does not fit. It is left out and named in a warning, and is never shortened. One that ends exactly at the next addition fits.
- A quick region may overlap the settled region of the same addition; the measurements they share are then counted in both.
- The average and the spread are worked out as for a settled region.

Example 1: a file of 30 min with additions at 10 and 20 min, $d = 0.5$ min and $q = 1$ min. The first quick region starts at $10 + 0.5 = 10.5$ min and ends at $10.5 + 1 = 11.5$ min. The second starts at 20.5 min and ends at 21.5 min.

Example 2: the same file with $q = 12$ min. The first would end at $10.5 + 12 = 22.5$ min, after the addition at 20 min, and the second at $20.5 + 12 = 32.5$ min, after the end of the file at 30 min: neither fits, and both are left out.

Checked by: `test_the_quick_windows_fall_after_the_additions` in `tests/test_averaging_windows.py`.

### 7.3 The change from the baseline

The change of a region, settled or quick, is measured from the one baseline of its file:

$$\text{difference} = m - m_0 \qquad p = \frac{m}{m_0} \times 100$$

- $m$: the average of the measurement in the region (in the unit of the measurement)
- $m_0$: its average in the baseline
- difference: in the unit of the measurement; worked out for the OCR, for every haem in every way it can be shown ($\Delta D$, absorbance, % oxidised) and for $\Delta\psi$
- $p$: the OCR as % of baseline (%), 100 meaning no change; worked out for the OCR only. A haem and $\Delta\psi$ have no percentage of the baseline: $\Delta D$ starts at 0, and the other levels can be near 0 or below it, where a percentage means nothing.

Each experiment's workbook gives these in its Averages sheet, one row per region: for the OCR the average, the spread, the difference and the % of baseline; for each haem, in each way it can be shown, the average, the spread and the difference (% oxidised only for a file with both regions); for $\Delta\psi$ the same three and the spectra used.

$\Delta\psi$ is empty wherever bH or bL is outside its limits (section 6), so a region can hold a $\Delta\psi$ for only some of its spectra. Its average and spread are taken over the spectra that have one, and "spectra used" says how many that was out of all the spectra of the region (5 of 9). A region with no $\Delta\psi$ at all is left empty (0 of 9).

Example 1: an OCR that averages 10 in the baseline (7.5 to 9.5 min), 4 in the quick region after the first addition (10.5 to 11.5 min) and 6 in the settled region before the second (17.5 to 19.5 min). The quick region gives a difference of $4 - 10 = -6$ and $p = \dfrac{4}{10} \times 100 = 40$ % of the baseline; the settled region gives $6 - 10 = -4$ and $p = \dfrac{6}{10} \times 100 = 60$ %.

Example 2: the haem bH in the same baseline and settled region. As $\Delta D$ it averages 0.5 and −2.0 mOD: a difference of $-2.0 - 0.5 = -2.5$ mOD. As absorbance, 12.5 and 10.0 mOD: $10.0 - 12.5 = -2.5$ mOD. As % oxidised, 80 and 50 %: $50 - 80 = -30$ (in % oxidised).

Example 3: $\Delta\psi$ averages 130 mV in the baseline. Of the nine spectra of the settled region the first four have no $\Delta\psi$ and the last five have 116, 116, 118, 120 and 120 mV. The average is

$$\frac{116 + 116 + 118 + 120 + 120}{5} = 118 \text{ mV}$$

the spread 2 mV, the difference $118 - 130 = -12$ mV, and the spectra used are 5 of 9.

Checked by: `test_both_kinds_are_averaged_from_one_baseline`, `test_every_haem_view_and_delta_psi_are_averaged` and `test_the_averages_sheet_holds_every_view` in `tests/test_averaging_windows.py`.

### 7.4 The OCR shown as % of baseline

The same percentage, taken at every time of the run and not only in the averaging regions, is one of the ways the OCR can be plotted (**OCR as** in the strip, question 5.3.1):

$$y = \frac{x}{b} \times 100$$

- $x$: the OCR at one time (µM min⁻¹)
- $b$: the average of the OCR in the baseline of that file (µM min⁻¹), the $m_0$ of 7.3
- $y$: the OCR at that time, in % of baseline; 100 where the OCR is what it was in the baseline, 0 where there is no oxygen consumption

- The OCR per OD gives the same $y$: the OD divides $x$ and $b$ alike.
- A file without a baseline (less than 10 s of data before its first addition, or no addition) has no % of baseline; so has a file whose $b$ is 0. Its plot keeps the OCR in µM min⁻¹ (per OD when OD values were entered), as its axis says.
- Each experiment's workbook gives $y$ in its sheet "OCR % of baseline", for every file with a baseline, and the baseline region and $b$ in "How it was worked out".

Example: an OCR of 10 µM min⁻¹ all through the baseline (7.5 to 9.5 min), so $b = 10$. Where the OCR is 10, $y = \dfrac{10}{10} \times 100 = 100$ %. Where it is 6, $y = \dfrac{6}{10} \times 100 = 60$ %. Where it is 2, $y = \dfrac{2}{10} \times 100 = 20$ %.

Checked by: `test_the_ocr_is_put_on_its_percent_of_baseline` in `tests/test_averaging_windows.py`.

### 7.5 A region set on its own

Any averaging region can be given its own length and its own gap (a settled region or the baseline) or its own start (a quick region). The equations of 7.1 and 7.2 stay the same; only the numbers put into them change for that region:

Settled region $i$:

$$\mathrm{end}_i = a_{i+1} - g_i \qquad \mathrm{start}_i = \mathrm{end}_i - w_i$$

Quick region $i$:

$$\mathrm{start}_i = a_i + d_i \qquad \mathrm{end}_i = \mathrm{start}_i + q_i$$

- $w_i$, $g_i$: the length and gap of settled region number $i$ (the baseline is $i = 0$); where it has none of its own, $w_i = w$ and $g_i = g$ of 7.1
- $d_i$, $q_i$: the start and length of quick region number $i$; where it has none of its own, $d_i = d$ and $q_i = q$ of 7.2
- The last settled region always ends $f$ before the end of the file ($\mathrm{end}_{\mathrm{last}} = T - f$): its own length is used, but it has no gap of its own, as nothing follows it. $f$ can be changed, and is the same in every file.

Notes:

- A settled or quick region can be left out with its tick. It is not averaged, and the figures leave a gap where it would be. Its row stays in the Averages sheet with its numbers empty and its kind marked "left out". The baseline cannot be left out, as every change is measured from it (7.3).
- A region set on its own is set in every file of the dataset, while "Apply to all" is ticked. Unticked (as it is at first, and again whenever another file is shown), only the file shown gets its own regions, and it keeps them however the others are changed.
- A region set on its own fits, or does not, by the same rules as in 7.1 and 7.2.

Example: a file of 30 min with additions at 10 and 20 min, $w = 2$ min, $g = 0.5$ min and $f = 1$ min.

- The baseline is set to 3 min long: it ends at $10 - 0.5 = 9.5$ min and starts at $9.5 - 3 = 6.5$ min.
- The region after the first addition is set to end 1.5 min before the next addition: it ends at $20 - 1.5 = 18.5$ min and starts at $18.5 - 2 = 16.5$ min.
- The last region is set to 4 min long: it ends at $30 - 1 = 29$ min and starts at $29 - 4 = 25$ min.
- With quick regions of $q = 1$ min starting $d = 0.5$ min after their addition, the first set to start 1 min after and last 0.5 min runs from $10 + 1 = 11$ min to $11 + 0.5 = 11.5$ min. The second, left out, would run from 20.5 to 21.5 min but is not averaged.

Checked by: `test_each_window_falls_on_its_own`, `test_a_window_left_out_keeps_its_row` and `test_each_file_finds_its_own_windows` in `tests/test_averaging_windows.py`.

---

## 8. The concentration of each addition

The labels table (question 3.3) takes, for each addition, the volume added, the concentration of the stock and the chemical (its label); it starts filled in from the text the instrument keeps with the addition (`1ul 8mm nd-011992` is $v = 1$ µL, $s = 8$ mM, nd-011992). The program works out the concentration in the chamber from them:

$$a = \frac{s\,v}{V} \qquad c = c_{\mathrm{before}} + a$$

- $s$: the concentration of the stock, typed in mM (or with its unit: nM, µM, mM or M), worked in µM
- $v$: the volume of stock added (µL)
- $V$: the volume of the chamber, always 5 mL = 5000 µL
- $a$: how much this addition raises the concentration in the chamber (µM)
- $c_{\mathrm{before}}$: the concentration in the chamber of the same thing before this addition (µM), 0 for its first addition. Two additions are of the same thing when their labels are alike once capitals, spaces and punctuation are left out ("KCN" and "kcn ")
- $c$: the concentration in the chamber after this addition (µM)

- The volume added is not counted in the chamber's volume: 10 µL in 5 mL makes the concentration read 0.2 % high, and three such additions 0.6 %.
- An addition with no stock and volume can have its concentration in the chamber typed by hand (in µM). It then counts as $c$, and $a = c - c_{\mathrm{before}}$.
- An event left out (labelled IGNORE) holds nothing and changes nothing.
- Each file is worked out on its own.
- The labels on the plots show $c$ ("In the chamber", the standard) or $v$ and $s$ ("What was added"), chosen with **Labels as** in the strip. $c$ is always written in µM and $s$ in mM, to four significant figures: 1200 µM stays 1200 µM, and a 1 M stock is 1000 mM.
- Each experiment's workbook gives $s$ (in mM), $v$, $a$ and $c$ in its Events sheet.

Example 1: 10 µL of a 200 mM KCN stock. $s = 200$ mM $= 200\,000$ µM, so

$$a = \frac{200\,000 \times 10}{5000} = 400 \text{ µM}$$

and $c = 0 + 400 = 400$ µM. The same again gives $c = 400 + 400 = 800$ µM, and a third time 1200 µM (shown as 1200 µM). 5 µL of a 10 mM BD stock in between gives $\dfrac{10\,000 \times 5}{5000} = 10$ µM of BD, and does not change the KCN.

Example 2: BD typed by hand as 10 µM in the chamber; then 5 µL of 10 mM BD gives $c = 10 + 10 = 20$ µM; then BD typed as 50 µM gives $a = 50 - 20 = 30$ µM.

Checked by: `test_one_addition`, `test_the_same_thing_added_again_adds_up`, `test_a_concentration_typed`, `test_a_stock_typed_with_its_unit`, `test_the_text_of_the_labels` and `test_the_text_in_the_file_read` in `tests/test_event_concentrations.py`.

---

## 9. The difference spectrum

The switch **Standard plot | Difference spectrum** under the boxes shows, for a file with both regions (section 3), how its spectrum changes from the oxidised region to the reduced region, and which haems make up that change.

$$\Delta A(w) = \overline{A(w)}_{\mathrm{red}} - \overline{A(w)}_{\mathrm{ox}}$$

- $w$: one wavelength (nm)
- $A(w)$: the attenuation of one spectrum at that wavelength, from 1.1, written in mOD (1 OD = 1000 mOD)
- $\overline{A(w)}_{\mathrm{red}}$: the mean of $A(w)$ over the spectra inside the reduced region (mOD); inside as in section 3, the spectra at both edges counted
- $\overline{A(w)}_{\mathrm{ox}}$: the same over the spectra inside the oxidised region (mOD)
- $\Delta A(w)$: the difference spectrum, reduced minus oxidised (mOD)

The difference is then described as so much of each haem's shape on top of a smooth background, exactly as one spectrum is in 1.2, with the background chosen for the dataset (1.3):

$$\Delta A = c_1 S_1 + c_2 S_2 + \dots + B$$

The plot shows $\Delta A$ in black, each haem's part $c_i S_i$ in its colour, $B$ dotted, the fit $c_1 S_1 + c_2 S_2 + \dots + B$ dashed, and underneath the residual $\Delta A$ minus the fit.

Notes:

- Each region's spectrum is the **mean** (average) of its spectra at each wavelength, while a haem's level in a region (section 3) is the **median** of its values there. So one spike in a spectrum moves the difference spectrum a little, where it would not move a level; the more spectra a region holds, the less.
- The shapes are oxidised minus reduced (1.2), so a haem more reduced in the reduced region has a negative amount $c$, and its part $c\,S$ follows the measured difference.
- A file without both regions has no difference spectrum, and keeps its standard plot.

Example: three wavelengths, 500, 550 and 600 nm. In the oxidised region, 0 to 1 min, three spectra: 400, 500, 600; 410, 510, 610; 420, 520, 620 mOD. A spectrum at 2 min (9000 mOD everywhere) lies in neither region and is left out. In the reduced region, 3 to 4 min: 412, 515, 610; 414, 517, 612; 416, 519, 614 mOD.

- Oxidised mean: $\dfrac{400 + 410 + 420}{3} = 410$, then 510 and 610 mOD.
- Reduced mean: $\dfrac{412 + 414 + 416}{3} = 414$, then 517 and 612 mOD.
- $\Delta A = 414 - 410 = 4$, $517 - 510 = 7$ and $612 - 610 = 2$ mOD.

Second example: a reduced spectrum built as the oxidised one plus the five haem shapes of 1.2 in the amounts 0.0001 to 0.0005 mM, and a background of 1 mOD plus a part falling from 2 mOD at the shortest wavelength to 0 at the longest. The decomposition of the difference gives back those five amounts, each haem's part as its amount times its shape, and a residual of 0.

Checked by: `test_mean_difference`, `test_known_haems_come_back` and `test_no_regions_no_difference` in `tests/test_difference_spectra.py`.

### 9.1 The haem bands

On the Difference spectrum and the Waterfall of a dataset figure, a shaded band in each haem's colour shows where that haem appears. A band comes from the haem's shape in the fit file alone, so it is the same on every plot and for every file, also for a haem a file has none of.

$$\text{band} = w_{\mathrm{peak}} - 2.5 \quad \text{to} \quad w_{\mathrm{peak}} + 2.5$$

- $w_{\mathrm{peak}}$: the wavelength where the haem's shape $S(w)$ is strongest, that is furthest from 0, whichever its sign (nm)
- 2.5: how far the band reaches each side (nm)

Example: a shape of 0, −3, 1, 0 at 540, 550, 560 and 570 nm is strongest (3) at 550 nm, so its band is 547.5 to 552.5 nm.

Checked by: `test_the_haem_bands` in `tests/test_difference_spectra.py`.

### 9.2 The waterfall

The Waterfall of a dataset figure stacks difference spectra, the first at the top, so their shapes can be compared. Nothing is stretched: each spectrum is only moved up or down, which is why its y axis has no numbers.

**The mean of the replicates.** As a time series, each line is the mean of the difference spectra of the experiments at one time point:

$$\overline{\Delta A}(w) = \frac{\Delta A_1(w) + \Delta A_2(w) + \dots + \Delta A_n(w)}{n}$$

- $\Delta A_1(w), \dots, \Delta A_n(w)$: the difference spectra of the $n$ experiments at that time point (mOD)
- $w$: one wavelength of the first experiment (nm)

An experiment measured at other wavelengths is first read at the wavelengths of the first, on the straight line between its own two nearest points:

$$y = y_1 + (y_2 - y_1) \times \frac{w - w_1}{w_2 - w_1}$$

- $w_1$, $w_2$: its two wavelengths either side of $w$ (nm); $y_1$, $y_2$: its values there (mOD)

Where an experiment does not reach a wavelength, the mean there is of the others.

Example: one spectrum is 1, 2, 3 mOD at 500, 510, 520 nm; another is 0, 2, 4 mOD at 495, 505, 515 nm. The second read at 500 nm is $0 + (2 - 0) \times \dfrac{5}{10} = 1$, at 510 nm it is 3, and it does not reach 520 nm. The mean is $\dfrac{1 + 1}{2} = 1$, $\dfrac{2 + 3}{2} = 2.5$, and 3 alone.

**Lining up and stacking.** Each spectrum is moved so that its highest point inside the band (9.1) of the haem picked in the form is at 0, then the spectra are spread out by one fixed gap:

$$y_{\mathrm{drawn}} = y - y_{\mathrm{top}} + (n - i) \times g, \qquad g = 0.75 \times h$$

- $y$: one point of the spectrum (mOD)
- $y_{\mathrm{top}}$: the highest point of that spectrum inside the band (mOD); the highest anywhere for a spectrum with no point in the band
- $i$: the place of the spectrum, 1 for the top one; $n$: how many spectra there are
- $h$: the height (highest minus lowest point) of the tallest spectrum (mOD); $g$: the gap between two neighbours

Example: at 540, 550, 560 and 570 nm, the top spectrum is 1, 5, 2, 9 and the second 0, 2, 4, 1 mOD, lined up on a band of 545 to 565 nm. The highest point of the first inside the band is 5 (the 9 is outside it), so it becomes −4, 0, −3, 4, which is 8 high; that of the second is 4, so it becomes −4, −2, 0, −3, which is 4 high. The gap is $0.75 \times 8 = 6$. The first is drawn at 2, 6, 3, 10 and the second, the last, stays at −4, −2, 0, −3.

Checked by: `test_spectra_averaged_and_stacked` in `tests/test_difference_spectra.py`, and `test_the_lines_of_a_waterfall` and `test_a_waterfall_drawn` in `tests/test_page_plots.py`.

A Waterfall can stack one trace per line in place of the difference spectrum (the OCR, a haem, the oxygen or $\Delta\psi$ against time). The traces are first lined up in time and, as a time series, averaged as in section 10; they are then stacked in the same way, with no band: each is moved so that its highest point anywhere is at 0.

Example: one line is 5 before the first addition and 2.5 after, the other 2 and 1. Moved, they are 0 and −2.5 (2.5 high) and 0 and −1 (1 high). The gap is $0.75 \times 2.5 = 1.875$, so the first is drawn at 1.875 and −0.625 and the second stays at 0 and −1.

Checked by: `test_a_waterfall_of_traces` in `tests/test_page_plots.py`.

---

## 10. Traces over time: the Single trace and the Mean trace

On a dataset figure, a Single trace shows one trace of one experiment, and a Mean trace the mean of the same trace over the experiments of each set. A trace is the measured oxygen, the OCR, one haem or $\Delta\psi$.

### 10.1 The value shown

A trace is shown in a value picked in the form of the plot. The OCR as measured (µM min⁻¹), per OD and as % of baseline (7.4), the haems as $\Delta D$ (section 2), absorbance (section 1) and % oxidised (section 4), and $\Delta\psi$ in mV (section 6) are read as the run worked them out. One value is new, for the OCR and for $\Delta\psi$, the change from baseline:

$$y = x - b$$

- $x$: the trace at one time (µM min⁻¹ for the OCR, mV for $\Delta\psi$)
- $b$: its average in the baseline of that file (the $m_0$ of 7.3), in the same unit
- $y$: what is drawn, in the same unit; 0 where the trace is what it was in the baseline

A file without a baseline has no change from baseline and no % of baseline, and is left out of the plot. The haems have neither (7.3).

Example: an OCR of 10, 10, 6 and 2 µM min⁻¹ with $b = 10$ is drawn at $10 - 10 = 0$, 0, $6 - 10 = -4$ and $2 - 10 = -8$ µM min⁻¹. A $\Delta\psi$ of 130, 126, 122 and 118 mV with $b = 130$ is drawn at 0, −4, −8 and −12 mV.

Checked by: `test_a_trace_in_each_value` in `tests/test_trace_alignment.py`.

### 10.2 Lining the experiments up

Each experiment has its own clock: its additions are not made at the same times as those of another, and the gap between two additions is not the same length. So the additions are the measuring stick. A Single trace only moves its clock:

$$t = x - a$$

- $x$: a time on the experiment's own clock (min)
- $a$: the time of the addition picked as time 0, on that clock (min); 0 when time 0 is the start of the recording
- $t$: the time on the plot (min)

A Mean trace puts every experiment on one shared time axis. On it, addition 1 of every experiment is at the same place, and so is addition 2, and so on. Up to halfway through the gap between two additions, a point is placed by its time after the addition before it; past halfway, by its time before the next one:

$$t = A_i + (x - a_i) \qquad \text{in the first half of the gap}$$

$$t = A_{i+1} - (a_{i+1} - x) \qquad \text{in the second half of the gap}$$

$$A_{i+1} = A_i + g_i$$

- $x$: a time on the experiment's own clock (min)
- $a_i$, $a_{i+1}$: the times of the additions before and after it, on that clock (min)
- $g_i$: the shortest gap $a_{i+1} - a_i$ among the experiments of the plot (min)
- $A_i$, $A_{i+1}$: where those two additions sit on the shared axis (min); the addition picked as time 0 is at 0
- $t$: the time on the shared axis (min); the two halves meet at $A_i + g_i / 2$

So a point 30 s before an addition is 30 s before it in every experiment, however long the gap was. Nothing is stretched: in an experiment whose gap is longer than the shortest, the spare middle of its gap is left out, and the lines and the time axis have a break mark (//) there. A break is marked only where a gap is more than 1 s longer than the shortest.

- Before the first addition a point is placed by its time before that addition, and after the last by its time after it. The axis goes as far each way as the shortest experiment does, so every point of a line is the mean of the same experiments.
- An experiment with another number of additions than most experiments of the plot is left out, as its additions cannot be matched to theirs, and is named in one warning when the figure is saved. So is one that has nothing for the trace and value picked.
- With time 0 at the start of the recording, the additions are not used: each experiment keeps its own clock, as far as they all go.
- When the addition picked is one the experiments do not have (addition 3 of two), the last one is time 0.

Example: experiment A has additions at 10 and 16 min (a gap of 6) and runs from 0 to 20 min; B has them at 12 and 17 min (a gap of 5) and runs to 25 min. With time 0 at the first addition, the shortest gap is $g = 5$, so the additions sit at $A_1 = 0$ and $A_2 = 5$ min, and the halves meet at 2.5 min.

- 1 min after addition 1 ($t = 1$): A's own time is $10 + 1 = 11$ min, B's is $12 + 1 = 13$ min.
- 30 s before addition 2 ($t = 5 - 0.5 = 4.5$): A's own time is $16 - 0.5 = 15.5$ min, B's is $17 - 0.5 = 16.5$ min.
- At the meeting point ($t = 2.5$): A's own time is $16 - 2.5 = 13.5$ min; one second earlier it was still counted from the first addition, just under $10 + 2.5 = 12.5$ min. A's minute from 12.5 to 13.5 is the spare middle, left out, with a break mark at 2.5. B has none: $12 + 2.5 = 14.5 = 17 - 2.5$.
- A has 10 min before its first addition and B 12, so the axis starts at −10. A has 4 min after its last and B 8, so it ends at $5 + 4 = 9$ min.

Checked by: `test_traces_are_lined_up_on_their_additions` and `test_another_number_of_additions_is_left_out` in `tests/test_trace_alignment.py`, and `test_a_single_trace_drawn` in `tests/test_page_plots.py`.

### 10.3 The mean and the band

Each lined-up trace is read once a second of the shared axis, on the straight line between its two nearest points (the equation of 9.2, with times in place of wavelengths). At each of those times:

$$\text{mean} = \frac{y_1 + y_2 + \dots + y_n}{n}$$

$$\mathrm{SD} = \sqrt{\frac{(y_1 - \text{mean})^2 + \dots + (y_n - \text{mean})^2}{n - 1}} \qquad \mathrm{SEM} = \frac{\mathrm{SD}}{\sqrt{n}}$$

- $y_1, \dots, y_n$: the values of the $n$ experiments of the set at that time, in the unit of the value shown
- mean: the line of the set
- SD: the spread of the experiments; SEM: the standard error of the mean. The band runs from mean − SEM to mean + SEM (or SD, as picked in the form)

A set of one experiment has a line and no band. Where an experiment has no value (a $\Delta\psi$ outside its limits, section 6), the mean there is of the others.

Example: three experiments read 4, 6 and 8. The mean is $\dfrac{4 + 6 + 8}{3} = 6$; the SD is $\sqrt{\dfrac{(-2)^2 + 0^2 + 2^2}{2}} = 2$; the SEM is $\dfrac{2}{\sqrt{3}} = 1.15$. The line is at 6 and its band from 4.85 to 7.15.

Checked by: `test_the_mean_and_the_band` in `tests/test_trace_alignment.py`, and `test_the_lines_of_a_mean_trace` and `test_a_mean_trace_drawn` in `tests/test_page_plots.py`.

---

## 11. Numbers per region, and their statistics

On a dataset figure, a plot per region (a Bar chart, Before and after, Response by region, Time points) shows one number per experiment for each averaging region (section 7), with the mean of each set of experiments, and tests whether the sets differ. The code is in `utils_shared/region_statistics.py`.

### 11.1 The value of an experiment in a region

$$v = \frac{y_1 + y_2 + \dots + y_k}{k}$$

- $y_1, \dots, y_k$: the trace, in the value picked in the form of the plot (10.1), at the $k$ times inside the region that have a number
- $v$: the value of the experiment in that region, in the unit of the value picked

So $v$ is the average of 7.3, and for the OCR its change from baseline and its % of baseline are the difference and the $p$ of 7.3. A haem is shown as $\Delta D$, absorbance or % oxidised, never as % of baseline or as a change from baseline (7.3). An experiment has no value in a region it does not have (fewer additions, a region that does not fit or was left out), and is then not counted in its set there.

Example: an OCR that is 10 µM min⁻¹ in the baseline, 4 in the quick region of the first addition and 6 in its settled region. In the settled region $v = 6$ µM min⁻¹ as measured, $6 - 10 = -4$ µM min⁻¹ as the change from baseline and $\dfrac{6}{10} \times 100 = 60$ % of baseline; in the quick region, 40 % of baseline. A $\Delta\psi$ of 130 mV in the baseline and 118 and 118 mV in the settled region gives $v = 118$ mV, or $118 - 130 = -12$ mV as the change from baseline.

Checked by: `test_the_value_of_an_experiment_in_a_region` in `tests/test_region_statistics.py`.

### 11.2 The mean, SD and SEM of a set

The equations of 10.3, with $y_1, \dots, y_n$ the values $v$ of the $n$ experiments of the set in one region. The bars of a plot run from mean − SEM to mean + SEM (or SD, as picked in the form). A set of one experiment has its dot and no bar.

Example, used in the rest of this section: the control experiments give 10, 11 and 12, and the knockdown experiments 20, 25 and 30.

- control: mean $\dfrac{10 + 11 + 12}{3} = 11$; SD $\sqrt{\dfrac{(-1)^2 + 0^2 + 1^2}{2}} = 1$; SEM $\dfrac{1}{\sqrt{3}} = 0.577$
- knockdown: mean 25; SD $\sqrt{\dfrac{(-5)^2 + 0^2 + 5^2}{2}} = 5$; SEM $\dfrac{5}{\sqrt{3}} = 2.887$

Checked by: `test_the_mean_sd_and_sem_of_a_set` in `tests/test_region_statistics.py`.

### 11.3 The t-test between two sets

Both tests compare the difference between the two means with how uncertain that difference is:

$$t = \frac{m_1 - m_2}{e}$$

- $m_1$, $m_2$: the means of the two sets
- $e$: the standard error of their difference, worked out in one of the two ways below
- $t$: how many standard errors apart the two means are; the further from 0, the smaller $p$

**Student's t-test** (the one a plot starts with) takes the two sets to scatter equally, and pools their two spreads into one:

$$s_p^2 = \frac{(n_1 - 1)\, s_1^2 + (n_2 - 1)\, s_2^2}{n_1 + n_2 - 2} \qquad e = \sqrt{s_p^2 \left( \frac{1}{n_1} + \frac{1}{n_2} \right)} \qquad \mathrm{df} = n_1 + n_2 - 2$$

**Welch's t-test** (the other choice in the form) keeps each set's own spread, and has fewer degrees of freedom the more the two spreads differ:

$$e = \sqrt{\frac{s_1^2}{n_1} + \frac{s_2^2}{n_2}} \qquad \mathrm{df} = \frac{\left( \dfrac{s_1^2}{n_1} + \dfrac{s_2^2}{n_2} \right)^2}{\dfrac{(s_1^2 / n_1)^2}{n_1 - 1} + \dfrac{(s_2^2 / n_2)^2}{n_2 - 1}}$$

- $n_1$, $n_2$: the number of experiments of each set
- $s_1$, $s_2$: the SD of each set (11.2)
- df: the degrees of freedom of the test
- $p$: the chance of a $t$ at least that far from 0, on either side (two-tailed), if the two sets really had the same mean; read from the t distribution with df degrees of freedom. In Excel, `=T.DIST.2T(ABS(t), df)` for Student's, and `=T.TEST(set 1, set 2, 2, 2)` (Student's) or `=T.TEST(set 1, set 2, 2, 3)` (Welch's) from the values themselves.

Notes:

- With the same number of experiments in both sets, the two tests give the same $t$, and differ only in df, so in $p$.
- A set of one experiment is not tested, as it has no SD. Nor are two sets that both have an SD of 0.
- With more than two sets, each pair of sets is tested.

Example: the control and knockdown sets of 11.2 ($m_1 = 11$, $s_1 = 1$, $m_2 = 25$, $s_2 = 5$, $n_1 = n_2 = 3$).

- Student's: $s_p^2 = \dfrac{2 \times 1 + 2 \times 25}{4} = 13$; $e = \sqrt{13 \times \dfrac{2}{3}} = 2.944$; $t = \dfrac{11 - 25}{2.944} = -4.756$; df $= 4$; $p = 0.0089$.
- Welch's: $e = \sqrt{\dfrac{1}{3} + \dfrac{25}{3}} = 2.944$, so the same $t = -4.756$; df $= \dfrac{8.667^2}{\dfrac{0.333^2}{2} + \dfrac{8.333^2}{2}} = \dfrac{75.11}{34.78} = 2.16$; $p = 0.0356$.

The knockdown set scatters five times more than the control, so Welch's trusts the difference less.

Checked by: `test_the_two_tests_between_sets` in `tests/test_region_statistics.py`, by hand and against the t-tests of the scipy library.

### 11.4 The paired t-test of Before and after

A Before and after plot compares two regions inside one set. Each experiment is compared with itself:

$$d_i = \text{after}_i - \text{before}_i \qquad t = \frac{\bar{d}}{s_d / \sqrt{n}} \qquad \mathrm{df} = n - 1$$

- $d_i$: the change of experiment $i$ from the first region to the second
- $\bar{d}$, $s_d$: the mean and the SD of those changes
- $n$: the number of experiments with a value in both regions
- $p$: read from $t$ and df as in 11.3; in Excel, `=T.TEST(before, after, 2, 1)`

A set with fewer than two such experiments is not tested.

Example: three experiments give 10, 12 and 14 before and 7, 8 and 12 after. The changes are −3, −4 and −2: $\bar{d} = -3$, $s_d = 1$, so $t = \dfrac{-3}{1 / \sqrt{3}} = -5.196$, df $= 2$ and $p = 0.0351$.

Checked by: `test_the_paired_test_of_before_and_after` in `tests/test_region_statistics.py`.

### 11.5 The Holm correction

Each test has a 1 in 20 chance of giving $p < 0.05$ by luck, so a plot with many tests would often have a mark that means nothing. The $p$ values of every test of one plot (every pair of sets in every region) are therefore corrected together. With the $m$ values sorted smallest first, $p_{(1)} \le p_{(2)} \le \dots \le p_{(m)}$:

$$p'_{(i)} = \min\left(1,\; \max\left(p'_{(i-1)},\; (m - i + 1) \times p_{(i)}\right)\right)$$

- $m$: the number of tests of the plot
- $p_{(i)}$: the $i$-th smallest $p$ value
- $p'_{(i)}$: its corrected value: the smallest is multiplied by $m$, the next by $m - 1$, and so on down to 1; a corrected value is never smaller than the one before it, and never above 1

A plot with one test is not changed by it. The marks are drawn from the corrected values.

Example 1: three tests give 0.01, 0.04 and 0.03. Sorted: 0.01, 0.03, 0.04. Corrected: $0.01 \times 3 = 0.03$; $0.03 \times 2 = 0.06$; $0.04 \times 1 = 0.04$, which is under the 0.06 before it, so 0.06. Only the first stays under 0.05.

Example 2: the control (10, 11, 12), knockdown (20, 25, 30) and rescue (11, 12, 13) sets in one region, by Student's t-test: control and knockdown $p = 0.0089$, knockdown and rescue 0.0115, control and rescue 0.2879. Corrected: $0.0089 \times 3 = 0.0268$; $0.0115 \times 2 = 0.0231$, raised to 0.0268; $0.2879 \times 1 = 0.2879$.

Checked by: `test_the_holm_correction` and `test_each_pair_of_sets_is_tested` in `tests/test_region_statistics.py`.

### 11.6 The marks

A comparison is marked only where its corrected $p$ is under 0.05: with stars (\* under 0.05, \*\* under 0.01, \*\*\* under 0.001) or with the value itself ("p = 0.018"; "p < 0.001" under 0.001), as picked in the form. A comparison that is not under 0.05, or was not tested, has no mark; "ns" is never written. The legend sentence under the page says what the bars are, how many experiments each set has, which set has only one, which test was used and how many tests the correction counted.

Example: corrected values of 0.0005, 0.005, 0.03 and 0.2 are marked \*\*\*, \*\*, \* and nothing.

Checked by: `test_the_marks` and `test_a_set_of_one_is_drawn_but_not_tested` in `tests/test_region_statistics.py`.
