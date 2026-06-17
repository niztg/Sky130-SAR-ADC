v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N -180 -50 -80 -50 {lab=#net1}
N -230 -30 -80 -30 {lab=#net2}
N -250 -10 -80 -10 {lab=#net3}
N -270 10 -80 10 {lab=0}
N -270 110 -180 110 {lab=0}
N -270 70 -270 110 {lab=0}
N -250 50 -250 110 {lab=0}
N -230 30 -230 110 {lab=0}
N -180 10 -180 110 {lab=0}
N 220 -50 240 -50 {lab=X}
N 220 -30 240 -30 {lab=xxx}
N 240 -50 270 -50 {lab=X}
N 270 -60 270 -50 {lab=X}
N 240 -30 270 -30 {lab=xxx}
N 270 -30 270 0 {lab=xxx}
C {strongarm_comparator.sym} 70 -20 0 0 {name=x1}
C {vsource.sym} -180 -20 0 0 {name=VDD value=1.8 savecurrent=false}
C {vsource.sym} -230 0 0 0 {name=CLK value=PULSE(0 1.8 10n 1n 1n 50n 100n) savecurrent=false}
C {vsource.sym} -250 20 0 0 {name=VIN1 value=0.95 savecurrent=false}
C {vsource.sym} -270 40 0 0 {name=VIN2 value=0.90 savecurrent=false}
C {gnd.sym} -270 110 0 0 {name=l1 lab=0}
C {lab_wire.sym} 270 -60 0 0 {name=p1 sig_type=std_logic lab=X}
C {lab_wire.sym} 270 0 0 0 {name=p2 sig_type=std_logic lab=Y}
