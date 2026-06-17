v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N -10 -110 680 -110 {lab=VDD}
N 20 -110 20 -50 {lab=VDD}
N 150 -110 150 -50 {lab=VDD}
N 280 -110 280 -50 {lab=VDD}
N 410 -110 410 -50 {lab=VDD}
N 530 -110 530 -50 {lab=VDD}
N 660 -110 660 -50 {lab=VDD}
N 20 -20 60 -20 {lab=VDD}
N 60 -110 60 -20 {lab=VDD}
N 150 -20 200 -20 {lab=VDD}
N 200 -110 200 -20 {lab=VDD}
N 340 -110 340 -20 {lab=VDD}
N 410 -20 460 -20 {lab=VDD}
N 460 -110 460 -20 {lab=VDD}
N 530 -20 580 -20 {lab=VDD}
N 580 -110 580 -20 {lab=VDD}
N 660 -20 680 -20 {lab=VDD}
N 680 -110 680 -20 {lab=VDD}
N -20 -20 -20 50 {lab=CLK}
N -30 50 -20 50 {lab=CLK}
N -20 50 110 50 {lab=CLK}
N 110 -20 110 50 {lab=CLK}
N 110 50 490 50 {lab=CLK}
N 490 -20 490 50 {lab=CLK}
N 490 50 620 50 {lab=CLK}
N 620 -20 620 50 {lab=CLK}
N 280 10 280 80 {lab=X}
N 280 30 370 -20 {lab=X}
N 410 10 410 80 {lab=Y}
N 320 -20 410 40 {lab=Y}
N 280 -20 340 -40 {lab=VDD}
N 280 110 280 120 {lab=0}
N 410 110 410 120 {lab=0}
N 350 120 410 120 {lab=0}
N 280 120 350 120 {lab=0}
N 280 30 370 110 {lab=X}
N 320 110 410 40 {lab=Y}
N 150 10 280 30 {lab=X}
N 410 40 530 10 {lab=Y}
N 20 10 280 180 {lab=P}
N 410 180 660 10 {lab=Q}
N 280 240 280 260 {lab=#net1}
N 280 260 410 260 {lab=#net1}
N 410 240 410 260 {lab=#net1}
N 340 260 340 270 {lab=#net1}
N 280 210 310 210 {lab=0}
N 310 120 310 210 {lab=0}
N 380 210 410 210 {lab=0}
N 380 120 380 210 {lab=0}
N 340 270 340 300 {lab=#net1}
N 340 330 380 330 {lab=0}
N 340 360 340 380 {lab=0}
N -20 330 300 330 {lab=CLK}
N -20 50 -20 330 {lab=CLK}
N 340 380 380 380 {lab=0}
N 380 330 380 380 {lab=0}
N 220 210 240 210 {lab=VIN1}
N 450 210 470 210 {lab=VIN2}
N 280 140 280 180 {lab=P}
N 410 140 410 180 {lab=Q}
N 210 170 280 170 {lab=P}
N 360 170 410 170 {lab=Q}
N 280 30 300 30 {lab=X}
N 410 40 450 40 {lab=Y}
C {sky130_fd_pr/pfet_01v8.sym} 0 -20 0 0 {name=S1
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
C {sky130_fd_pr/pfet_01v8.sym} 130 -20 0 0 {name=S3
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
C {sky130_fd_pr/pfet_01v8.sym} 300 -20 0 1 {name=M5
W=4
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
C {sky130_fd_pr/pfet_01v8.sym} 390 -20 0 0 {name=M6
W=4
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
C {sky130_fd_pr/pfet_01v8.sym} 510 -20 0 0 {name=S4
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
C {sky130_fd_pr/pfet_01v8.sym} 640 -20 0 0 {name=S2
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
C {ipin.sym} -10 -110 0 0 {name=p1 lab=VDD}
C {ipin.sym} -30 50 0 0 {name=p2 lab=CLK}
C {sky130_fd_pr/nfet_01v8.sym} 390 110 0 0 {name=M4
W=4
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
C {sky130_fd_pr/nfet_01v8.sym} 300 110 0 1 {name=M3
W=4
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
C {gnd.sym} 350 120 0 0 {name=l1 lab=0}
C {sky130_fd_pr/nfet_01v8.sym} 260 210 0 0 {name=M1
W=8
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
C {sky130_fd_pr/nfet_01v8.sym} 430 210 0 1 {name=M2
W=8
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
C {sky130_fd_pr/nfet_01v8.sym} 320 330 0 0 {name=M7
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
model=nfet_01v8
spiceprefix=X
}
C {gnd.sym} 340 380 0 0 {name=l2 lab=0}
C {ipin.sym} 220 210 0 0 {name=p3 lab=VIN1}
C {ipin.sym} 470 210 0 1 {name=p4 lab=VIN2}
C {lab_pin.sym} 210 170 0 0 {name=p7 sig_type=std_logic lab=P}
C {lab_pin.sym} 360 170 0 0 {name=p8 sig_type=std_logic lab=Q}
C {opin.sym} 300 30 0 0 {name=p5 lab=X}
C {opin.sym} 450 40 0 0 {name=p6 lab=Y}
