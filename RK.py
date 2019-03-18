import numpy as np
from data_collection import Input, Output
import datetime
#Initialization

grid = "insteggerd grid"
BC = "boundary condition u,v, tp, qv, gp', and μ'd"

height
p_dry_top, p_sd"grid"
gp_surface

nX"const"
nY"const"
nK = 26 "equals to the numbers of vertical isobaric layers from global model"
idxK"grid of vertical eta index"

edge = (N,E,S,W) "(grid, grid, grid, grid)"
lat = (edge[0]-edge[2])/2

wd = (wdK, wdY, wdK)

mapFactorX = 1, mapFactorY = 1

t_start = datetime.datetime() 
t_end = datetime.datetime()
ns = 
Step = datetime.timedelta(seconds = )
Step_RK3 = datetime.timedelta(seconds = ) # 6*wdX sec is suggested

g = 9.81
Rd = 287 #J/kg/K
Rv = 461.6 #J/kg/K
p0 = 10^5 #pa
T0 = 300 #K, mean sea level temp
A = 50 #K, difference between p0 and p0/e
Omega = 7.2921*10^-5 #sec^-1
rEarth = 6.307*10^6 #meter
rotationAngle = "ang_r"
Beta = 0.1
MW_wv = "molecular weight of water vapor"
MW_dry = "molecular weight of dry air"
epcilon = MW_wv/MW_dry

u = Input("u", t_now), v = Input("v", t_now), w = Input("w", t_now),o = Input("o", t_now),
tp = Input("tp",t_now),  gp = Input("gp", t_now),
qv = Input("qv", t_now), qc = Input("qc", t_now), qr = Input("qr", t_now), qi = Input("qi", t_now)
qm = qv+qc+qr+qi
D = Ddry()/(1+qm)

"Remember to revise U,V mapFactor in and Mdry during acoustic step"
U = coupled(u), V = coupled(v), W = coupled(w), O = coupled(o), Tp = coupled(tp),
Qv = coupled(qv), Qc = coupled(qc), Qr = coupled(qr), Qi = coupled(qi), Qm = coupled(qm)

#Runge-Kutta Step	main-loop
def main():
	for t in range(0, (t_end-t_start)/Step): 
		t_now = t_start + t*Step
			
		for i in range(3,0,-1):
			RK3_start = t_now

			if i == 3:
				n = 1, Step_acoustic = Step_RK3/3

				U_tend = Adv("U")+Fcor("U")
				V_tend = Adv("V")+Fcor("V")
				W_tend = Adv("W")+Fcor("W")
				Tp_tend = Adv("Tp")+Fcor("Tp")
				gp_tend = Adv("gp")+Fcor("gp")
				Mdry_tend = Adv("Mdry")+Fcor("Mdry")
				
			else:
				n = ns/i, Step_acoustic = Step_RK3/ns

			var_S = (
					ModeS("U", U_tend),
					ModeS("V", V_tend),
					ModeS("W", W_tend),
					ModeS("Mdry", Mdry_tend),
					ModeS("Tp", Tp_tend),
					ModeS("gp", gp_tend)
					)

			acoustic_time_integration(var_S, n, RK3_start, Step_acoustic)

			Qm_tend = - mapFactorX*mapFactorY*(Spatial(timeAvg("U", acoustic_start, Step_acoustic*n)*Interp(qm, 2), 2) + Spatial(timeAvg("V", acoustic_start, Step_acoustic*n)*Interp(qm, 1), 1)) - mapFactorY*Spatial(timeAvg("O", acoustic_start, Step_acoustic*n)*Interp(qm, 0), 0)
			Qm_advanced = Input("Qm", RK3_start) + Step_RK3*Qm_tend

			p = p_moist()
			gp_perturb_from_refer_grad = -(Mdry_reference()*Ddry_perturb_from_refer()+Mdry*Ddry_reference())

			Output("Qm", Qm_advanced, RK3_start + n*Step_acoustic)
			Output("p", p, RK3_start + n*Step_acoustic)
			Output("Ddry", Ddry, RK3_start + n*Step_acoustic)


#reference state
def cp():
    global Rd
	c_p= 7*Rd/2
	return c_p

def cv():
	global Rd
	c_v = cp()−Rd
	return c_v

def gamma():
    gma = cp()/cv()
	return gma

def cs_sqr():
	global p,Ddry
	cs2 = gamma()*p*Ddry
	return cs2

def p_dry_surface():
	global A, p0, T0, Rd, gp_surface
	pdhs = p0*np.exp(-T0/A+((T0/A)^2-2*gp_surface/A/Rd)^0.5)
	return pdhs

def p_reference():
	global K
	pdr = K*Mdry_reference()+p_dry_top
	return pdr

def T_reference():
	global A, p0, T0
	Tr = T0+A*np.log(p_reference()/p0)
	return Tr

def tp_reference():
	global T0, A, p0, Rd
	tpdr = (T0+A*np.log(p_reference()/p0))*(p0/p_reference())^(Rd/cp())
	return tpdr

def Ddry_reference():
	global p0, Rd
	Ddr = Rd*tp_reference()/p0*(p_reference()/p0)^(-cv()/cp())
	return Ddr

def Mdry_reference():
	Mdr = p_dry_surface()-p_dry_top
	return Mdr

def gp_reference_grad():
	grad = Ddry_reference()*Mdry_reference()
	return grad

def gp_reference():
	gpr = Interp(gp_reference_grad(), 0)

#perturbation state from reference
def Mdry():
	global p_sd
	Md = p_sd - p_dry_surface()
	return Md

def Mdry_perturb_from_refer():
	Md_pfr = Mdry() - Mdry_reference()
	return Md_pfr

def p_perturb_from_refer_grad(): 
	grad = Mdry_perturb_from_refer()*(1+Interp(qv, 0))+Interp(qv, 0)*Mdry_reference()
	return grad

def p_perturb_from_refer():
	p_pfr = Interp(p_perturb_from_refer_grad(), 0)
	return p_pfr

def Ddry():
	global Rd, Rv, p0, tp
	Dd = Rd/p0*tp*(1+Rv/Rd*qv)*(p_perturb_from_refer() + p_reference()/p0)^(-cv()/cp())
	return Dd

def Ddry_perturb_from_refer():
	Dd_pfr = Ddry() - Ddry_reference()
	return Dd_pfr

def gp_perturb_from_refer_grad():
	grad = -(Mdry()*Ddry_perturb_from_refer()+Mdry_perturb_from_refer()*Ddry_reference())
	return grad

def gp_perturb_from_refer ():
	gp_pfr = Interp(gp_perturb_from_refer_grad(), 0)
	return gp_pfr 

#diagnostic eq
def tp_moist():
	global tp, qv
	tp_m = tp*(1+(Rv/Rd)*qv)
	return tp_m

def p_moist():
	global p0, Ddry
	pressure = p0*(Rd*tp_moist()/p0/Ddry)^gamma()
	return pressure 


#level identification
def level_determine(var):
	global nX, nY, nK

	if len(var) == nK and len(var[0]) == nY and len(var[0][0]) == nX:
			lvl = "mp"
	elif len(var) == nK and len(var[0]) == nY and len(var[0][0]) == nX+1:
			lvl = "u"
	elif len(var) == nK and len(var[0]) == nY+1 and len(var[0][0]) == nX:
			lvl = "v"
	elif len(var) == nK+1 and len(var[0]) == nY and len(var[0][0]) == nX:
			lvl = "w"
	
	return lvl

#import variable and turn it to coupled form
def coupled(var):# a is any variable
	global Mdry, mapFactorX, mapFactorY

	if level_determine(var) == "mp":
		M = Mdry, mF = 1
	elif level_determine(var) == "u":
		M = Interp(Mdry,2), mf = Interp(mapFactorY, 2)
	elif level_determine(var) == "v":
		M = Interp(Mdry,1), mf = Interp(mapFactorX, 1)
	elif level_determine(var) == "w":
		M = Mdry, mf = mapFactorY
	Var = M*var/mF

	return Var

def uncoupled(Var):
	global Mdry
	if level_determine(var) == "mp":
		M = Mdry, mF = 1
	elif level_determine(var) == "u":
		M = Interp(Mdry,2), mf = Interp(mapFactorY, 2)
	elif level_determine(var) == "v":
		M = Interp(Mdry,1), mf = Interp(mapFactorX, 1)
	elif level_determine(var) == "w":
		M = Mdry, mf = mapFactorY
	var = *mf*Var/M

	return var

#Operator
def timeAvg(name, var_advanced, start, Step):
	global Beta
	var_prev = Input(name, start - step)
	var_timeAvg = (1+Beta)/2*var_advanced+(1-Beta)/2*var_prev

	return var_timeAvg

def Interp(var, axis):#x is supposed to be a tuple
	global wdK
	if level_determine(var) == "mp":
		wd_forward = np.concatenate((wd[axis], bc), axis)
		wd_backward = np.concatenate((bc, wd[axis]), axis)
		
		var_forward = np.concatenate((var, bc), axis)
		var_backward = np.concatenate((bc, var), axis)
		
		Var = 0.5*(wd_backward/(0.5*(wd_backward + wd_forward))*var_forward + wd_forward/(0.5*(wd_backward + wd_forward))*var_backward)
	else:
		var_forward = var.take(np.arange(1, var.shape[axis]), axis)
		var_backward = var.take(np.arange(0, var.shape[axis]-1), axis)
		
		Var = 0.5*(var_forward + var_backward)	
	
	return Var

def Spatial(var, axis):#axis option (x,y)
	global wdX, wdY, BC

	if level_determine(var) == "mp":
		var_forward = np.concatenate((var.take(np.arange(1, var.shape[axis]), axis), bc), axis)/2
		var_backward = np.concatenate((bc, var.take(np.arange(0, var.shape[axis]-1), axis)), axis)/2
	else:
		var_forward = var.take(np.arange(1, var.shape[axis]), axis)
		var_backward = var.take(np.arange(0, var.shape[axis]-1), axis)

	Var = (var_forward - var_backward)/wd[axis]

	return Var
	
def Vert_Integrat(var):
	global wdK

	product = 0

	for i in range(0, len(var)):
		product += var[i]
	product = np.expand_dims(product, 0)

	rearrange = np.array([])
	for j in range(0, len(var)):
		if j = 0:
			rearrange = np.concatenate((product, product), 0)
		else:
			rearrange = np.concatenate((rearrange, product), 0)
	return product

#tend Term
def Fcor(var):#axis is supposed to be "U", "V" or "W"
	global lat, Omega, rEarth, mapFactorX, mapFactorY, rotationAngle, U, V, W,
	e = 2*Omega*np.cos(lat)
	f = 2*Omega*np.sin(lat)

	if var == "U":
		Vxy = Interp(Interp(V,1),2)
		Wxk = Interp(Interp(W,0),2)
		tend = Vxy*(
			Interp(f,2) 
			+ Interp((Interp(uncouple(U),2)*Spatial(mapFactorY,1)
				- Interp(uncouple(V),1)*Spatial(mapFactorX,2)),2)
			)
			- Interp(e,2)*Wxk*Interp(np.cos(rotationAngle), 2)
			- uncouple(U)*Wxk/rEarth

	elif var == "V":
		Uxy = Interp(Interp(U,2),1)
		Wyk = Interp(Interp(W,0),1)
		tend = - Uxy*(
			Interp(f,1) 
			+ Interp((Interp(uncople(U),2)*Spatial(mapFactorY,1)
				- Interp(uncouple(V),1)*Spatial(mapFactorX,2)),1)
			)
			+ Interp(e,1)*Wyk*Interp(np.sin(rotationAngle), 1)
			- uncouple(V)*Wyk/rEarth

	elif var == "W":
		Uxk = Interp(Interp(U,2),0)
		Vyk = Interp(Interp(V,1),0)
		tend = e*(
			Uxk*np.cos(rotationAngle)
			- Vyk*np.sin(rotationAngle)
			)
			+ (
				Interp(Interp(uncouple(U),2),0)*Uxk
				+ Interp(Interp(uncouple(V),1),0)*Vyk
				)/rEarth

	else:
		tend = 0

	return tend

def Adv(var):
	global mapFactorX, mapFactorY, U, V, O, gp, acoustic_start, Step_acoustic, ns
	if var == "U":
		tend = - mapFactorX*(Spatial(U*uncoupled(U), 2) + Spatial(V*uncoupled(U), 1)) - Spatial(O*uncoupled(U), 0)
	elif var == "V":
		tend = - mapFactorY*(Spatial(U*uncoupled(V), 2) + Spatial(V*uncoupled(V), 1)) - mapFactorX/mapFactorY*Spatial(O*uncoupled(V), 0)
	elif var == "Mdry":
		tend = - mapFactorX*mapFactorY*(Spatial(U, 2) + Spatial(V, 1)) - mapFactorY*Spatial(O, 0)
	elif var == "Tp":
		tend = - mapFactorX*mapFactorY*(Spatial(U*Interp(uncoupled(Tp)), 2) + Spatial(V*Interp(uncoupled(Tp)), 1)) - mapFactorY*Spatial(O*uncoupled(Tp), 0)
	elif var == "W":
		tend = - mapFactorX*mapFactorY/mapFactorY*(Spatial(U*uncoupled(W), 2) + Spatial(V*uncoupled(W), 1)) - Spatial(O*uncoupled(W), 0)
	elif var == "gp":
		tend = - (mapFactorX*mapFactorY*(U*Spatial(gp, 2) + V*Spatial(gp, 1)) + mapFactorY*O*Spatial(gp, 0))/Mdry
	else:
		tend = 0

	return tend

#Time integration
#O doesn't join time integration
def ModeS(var, tend):
	global mapFactorX, mapFactorY, U, V, O, gp, D

	if var == "U":
		S = -(Interp(Mdry,2)*Interp(D,2)*Spatial(p_perturb_from_refer,2)
			-Interp(Mdry,2)*Interp(D_perturb_from_refer,2)*Spatial(p_reference(),2)) 
			-Interp(D/Ddry, 2)
			*(Interp(Mdry,2)*Spatial(Interp(gp_perturb_from_refer,0),2)
				-Spatial(Interp(Interp(p_perturb_from_refer,0),2),0)*Spatial(Interp(gp,0),2)
				+Interp(Mdry_perturb_from_refer,2)*Spatial(Interp(gp,0),2))
			+ tend

	elif var == "V":
		S = -(Interp(Mdry,1)*Interp(D,1)*Spatial(p_perturb_from_refer,1)
			-Interp(Mdry,1)*Interp(D_perturb_from_refer,1)*Spatial(p_referemce(),1)) 
			-Interp(D/Ddry, 1)
			*(Interp(Mdry,1)*Spatial(Interp(gp_perturb_from_refer,0),1)
				-Spatial(Interp(Interp(p_perturb_from_refer,0),1),0)*Spatial(Interp(gp,0),1)
				+Interp(Mdry_perturb_from_refer,1)*Spatial(Interp(gp,0),1)) 
			+ tend

	elif var == "Mdry":
		S =  tend

	elif var == "Tp":
		S =  tend

	elif var == "W":
		S = g*(Interp(D/Ddry, 0)*(Spatial(p_perturb_from_refer,0)+M_referemce()*Interp(qr+qc+qv,0))-Mdry_perturb_from_refer)/mapFactorY 
			+ tend

	elif var == "gp":
		S = mapFactorY*g*W/Mdry
			+ tend
	
	return S

def ModeF(var, acoustic_start):
	global mapFactorX, mapFactorY, U, V, O, gp, D

	if var == "U":
		F = Interp(M,2)*Interp(D,2)*Spatial(Input(p_perturb, acoustic_start), 2)
		  + (Interp(M,2)*Spatial(p_reference(),2)*Interp(Input(D_perturb, acoustic_start),2))
		  + Interp(D/Ddry, 2)*
		  (
		  	Interp(M,2)*Spatial(Interp(Input(gp_perturb, acoustic_start), 0),2)
		  	+ Spatial(Interp(gp, 0),2)*
		  	(
		  		Spatial(Interp(Interp(Input(p_perturb, acoustic_start),0),2),0)
		  		-Interp(Input(M_perturb ,acoustic_start),2)
		  		)

		  	)

	elif var == "V":
		F = Interp(M,1)*Interp(D,1)*Spatial(Input(p_perturb, acoustic_start),1)
		  + (Interp(M,1)*Spatial(p_reference(),1)*Interp(Input(D_perturb, acoustic_start),1))
		  + Interp(D/Ddry, 1)*
		  (
		  	Interp(M,1)*Spatial(Interp(Input(gp_perturb, acoustic_start), 0),1)
		  	+Spatial(Interp(gp, 0),1)*
		  	(
		  		Spatial(Interp(Interp(Input(p_perturb, acoustic_start),0),1),0)
		  		-Interp(Input(M_perturb,acoustic_start),1)
		  		)
		  	)

	

def acoustic_time_integration(var_S, n, RK3_start, Step_acoustic):
	global   U, V, W, Mdry, Tp, O, gp, p, D, Ddry, M

	U_S = var_S[0], V_S = var_S[1], W_S = var_S[2],
	Mdry_S = var_S[3], Tp_S = var_S[4], gp_S = var_S[5]
	
	acoustic_start = RK3_start 
	
	U_perturb = U - Input("U", acoustic_start)
	V_perturb = V - Input("V", acoustic_start)
	W_perturb = W - Input("W", acoustic_start)
	Mdry_perturb = Mdry - Input("Mdry", acoustic_start)
	Tp_perturb = Tp - Input("Tp", acoustic_start)
	gp_perturb = gp - Input("gp", acoustic_start)

	for j in range(0, n):
		U_perturb = U_perturb + Step_acoustic*( U_S - ModeF("U",acoustic_start))
		V_perturb = V_perturb + Step_acoustic*(V_S - ModeF("V",acoustic_start))

		Mdry_perturb_difference = mapFactorX*mapFactorY*Vert_Integrat(Spatial(U_perturb, 2) + Spatial(V_perturb, 1))
		
		Mdry_perturb = Mdry_perturb + Step_acoustic*Mdry_perturb_difference 		  
		O_perturb = Vert_Integrat(Mdry_S - Mdry_perturb_difference - mapFactorX*mapFactorY*(Spatial(U_perturb, 2) + Spatial(V_perturb, 1)))/mapFactorY
		Tp_perturb = Tp_perturb + Step_acoustic*(Tp_S - (mapFactorX*mapFactorY*(Spatial(U_perturb*tp,2)+Spatial(V_perturb*tp,1))+mapFactorY*Spatial(O_perturb*tp,0)))
		 

		W_perturb = W_perturb + Step_acoustic*(W_S  + g/mapFactorY*(D/Ddry)*()-timeAvg(Mdry_perturb))
		gp_perturb = gp_perturb + Step_acoustic*(gp_S - ()/Mdry)
		 
		#diagnostic equation
		C = cs_sqr/Mdry_perturb/Ddry^2
		Ddry_perturb = -(Spatial(gp_perturb ,0) + Ddry*Mdry_perturb)/Mdry
		p_perturb = cs_sqr/Ddry*(Tp_perturb/Tp - Ddry_perturb/Ddry - Mdry_perturb/Mdry)

		acoustic_end = RK3_start + (j+1)*Step_acoustic
		acoustic_start = acoustic_end

		Output("U_perturb", U_perturb, acoustic_end)
		Output("V_perturb", V_perturb, acoustic_end)
		Output("W_perturb", W_perturb, acoustic_end)
		Output("O_perturb", O_perturb, acoustic_end)
		Output("Mdry_perturb", Mdry_perturb, acoustic_end)
		Output("Tp_perturb", Tp_perturb, acoustic_end)
		Output("gp_perturb", gp_perturb, acoustic_end)
		Output("Ddry_perturb", Ddry_perturb, acoustic_end)
		Output("p_perturb", p_perturb, acoustic_end)


	Output("U", uncouple(U_perturb+U), acoustic_end)
	Output("V", uncouple(V_perturb+V), acoustic_end)
	Output("W", uncouple(W_perturb+W), acoustic_end)
	Output("O", uncouple(O_perturb+O), acoustic_end)
	Output("Mdry", Mdry_perturb+Mdry, acoustic_end)
	Output("Tp", uncouple(Tp_perturb+Tp), acoustic_end)
	Output("gp", gp_perturb+gp, acoustic_end)

