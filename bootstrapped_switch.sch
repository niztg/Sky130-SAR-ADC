v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N -10 -110 60 -110 {lab=#net1}
N -210 -50 -210 -10 {lab=#net2}
N -210 -10 -150 -10 {lab=#net2}
N -120 -110 -120 -50 {lab=#net1}
N -120 -110 -10 -110 {lab=#net1}
N -210 -190 -210 -110 {lab=#net3}
N -210 -190 -130 -190 {lab=#net3}
N -70 -190 -0 -190 {lab=#net1}
N -0 -190 -0 -110 {lab=#net1}
N -90 -10 -30 -10 {lab=VIN}
N -280 -190 -210 -190 {lab=#net3}
N -310 -280 -310 -230 {lab=#net1}
N -310 -280 0 -280 {lab=#net1}
N 0 -280 0 -190 {lab=#net1}
N -400 -190 -340 -190 {lab=VDD}
N -280 -10 -210 -10 {lab=#net2}
N -410 -10 -340 -10 {lab=0}
N -420 -190 -400 -190 {lab=VDD}
N 30 -10 90 -10 {lab=VOUT}
N 90 -10 90 30 {lab=VOUT}
N -420 -70 -310 -70 {lab=PHIBAR}
N -310 -70 -310 -50 {lab=PHIBAR}
N -310 -120 -310 -70 {lab=PHIBAR}
N -310 -120 -240 -120 {lab=PHIBAR}
N -240 -240 -240 -120 {lab=PHIBAR}
N -240 -240 -100 -240 {lab=PHIBAR}
N -100 -240 -100 -230 {lab=PHIBAR}
N -310 -10 -310 -0 {lab=0}
N -120 -10 -120 10 {lab=0}
N 0 -20 -0 -10 {lab=0}
N -0 -20 150 -20 {lab=0}
N 120 -110 150 -110 {lab=0}
N 150 -110 150 -20 {lab=0}
N -30 -10 -30 80 {lab=VIN}
N -0 30 -0 80 {lab=#net1}
N 0 80 240 80 {lab=#net1}
N 240 -190 240 80 {lab=#net1}
N 0 -190 240 -190 {lab=#net1}
N 90 -130 90 -110 {lab=0}
N 90 -130 150 -130 {lab=0}
N 150 -130 150 -110 {lab=0}
N -160 -340 -160 -240 {lab=PHIBAR}
N -160 -340 200 -340 {lab=PHIBAR}
N 200 -340 200 -70 {lab=PHIBAR}
N 90 -70 200 -70 {lab=PHIBAR}
N -260 200 -120 -80 {lab=#net1}
N -230 240 300 240 {lab=VDD}
N -400 -420 -400 -190 {lab=VDD}
N -400 -420 310 -420 {lab=VDD}
N 300 240 310 -420 {lab=VDD}
N -260 340 -180 240 {lab=VDD}
N -230 380 -120 380 {lab=#net1}
N -120 160 -120 380 {lab=#net1}
N -240 160 -120 160 {lab=#net1}
N -360 240 -290 240 {lab=#net4}
N -360 240 -360 380 {lab=#net4}
N -360 380 -290 380 {lab=#net4}
N -360 290 -260 240 {lab=#net4}
N -360 290 -260 380 {lab=#net4}
N -100 -190 -100 -170 {lab=#net4}
N -310 -190 -310 -170 {lab=#net4}
N -310 -170 -100 -170 {lab=#net4}
N -310 240 -230 -170 {lab=#net4}
C {sky130_fd_pr/nfet_01v8.sym} 0 10 3 0 {name=Q0
W=1
L=0.15
nf=1 
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/cap_mim_m3_1.sym} -210 -80 0 0 {name=C_boot model=cap_mim_m3_1 W=15.6 L=15.6 MF=1 spiceprefix=X}
C {sky130_fd_pr/nfet_01v8.sym} 90 -90 3 0 {name=Q5
W=1
L=0.15
nf=1 
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} -120 -30 1 0 {name=Q4
W=1
L=0.15
nf=1 
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} -310 -210 1 0 {name=Q1
W=2
L=0.15
nf=1
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} -310 -30 1 0 {name=Q3
W=1
L=0.15
nf=1 
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {ipin.sym} -420 -190 0 0 {name=p1 lab=VDD}
C {gnd.sym} 150 -20 0 0 {name=l1 lab=0}
C {gnd.sym} -410 -10 0 0 {name=l2 lab=0}
C {ipin.sym} -30 80 0 0 {name=p2 lab=VIN}
C {ipin.sym} 90 30 0 0 {name=p3 lab=VOUT}
C {ipin.sym} -420 -70 0 0 {name=p4 lab=PHIBAR}
C {sky130_fd_pr/pfet_01v8.sym} -100 -210 1 0 {name=Q2
W=1
L=0.15
nf=1
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {gnd.sym} -310 0 0 0 {name=l3 lab=0}
C {gnd.sym} -120 10 0 0 {name=l4 lab=0}
C {sky130_fd_pr/pfet_01v8.sym} -260 220 1 0 {name=XWA
W=1
L=0.15
nf=1
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/pfet_01v8.sym} -260 360 1 0 {name=XWB
W=1
L=0.15
nf=1
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
