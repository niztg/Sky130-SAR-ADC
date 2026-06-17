v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N -110 -80 -20 -80 {lab=#net1}
N -110 -20 -110 -0 {lab=0}
N -20 -20 -20 20 {lab=#net2}
N -110 0 -110 170 {lab=0}
N -110 170 -20 170 {lab=0}
N -20 80 -20 170 {lab=0}
N -70 -60 -70 30 {lab=#net3}
N -70 -60 -20 -60 {lab=#net3}
N -70 90 -70 170 {lab=0}
N -180 -40 -20 -40 {lab=#net4}
N -180 20 -180 170 {lab=0}
N -180 170 -110 170 {lab=0}
C {bootstrapped_switch.sym} 130 -50 0 0 {name=x1}
C {vsource.sym} -110 -50 0 0 {name=V1 value=1.8 savecurrent=false}
C {gnd.sym} -110 170 0 0 {name=l1 lab=0}
C {vsource.sym} -20 50 0 0 {name=V2 value='SIN(0.9 0.9 100k)' savecurrent=false}
C {vsource.sym} -70 60 0 0 {name=V3 value='PULSE(1.8 0 0 1n 1n 300n 1000n)' savecurrent=false}
C {capa.sym} -180 -10 0 0 {name=C1
m=1
value=25.6p
footprint=1206
device="ceramic capacitor"}
C {code_shown.sym} 100 80 0 0 {name=s1 only_toplevel=false value=
.tran 1n 20u
.lib /Users/nizansari/.volare/sky130A/libs.tech/ngspice/sky130.lib.spice tt}
