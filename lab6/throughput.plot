set xlabel "time [s]"
set ylabel "Throughput [Mbps]"
set key bel
plot  "tcp1.tr" u 1:2 t "TCP1" w lp lt rgb "blue", "tcp2.tr" u 1:2 t "TCP2" w lp lt rgb "red"
pause -1
