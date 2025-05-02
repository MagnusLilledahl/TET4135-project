set terminal postscript eps font 'Helvetica,20'
set output "xcoeff.eps"
set key off
set title "Inital payement / x-coefficient"
set xlabel "x-coefficient"
set ylabel "Inital payement [MNOK]"

plot "P0-xcoeff.dat" using 1:($2/1e6) with lines lc 8

set output "discount.eps"
set title "Inital payement / discount rate"
set xlabel "discount rate"
set ylabel "Inital payement [MNOK]"

plot "P0-discount.dat" using 1:($2/1e6) with lines lc 8

set output "charging.eps"
set title "Inital payement / charging rate"
set xlabel "Change in coefficient"
set ylabel "Inital payement [MNOK]"

plot "P0-charging.dat" using 1:($2/1e6) with lines lc 8

set output "peak.eps"
set title "Inital payement / Peak energy price"
set xlabel "Change in coefficient"
set ylabel "Inital payement [MNOK]"

plot "P0-peak.dat" using 1:($2/1e6) with lines lc 8