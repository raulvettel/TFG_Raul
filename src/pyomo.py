from pyomo.environ import * # For Pyomo 4.0 & later
from pyomo.opt import SolverFactory, SolverManagerFactory

# from coopr.pyomo import * # For earlier versions

model = AbstractModel()




## Define sets
model.proveedores = Set()
model.dias = Set()
model.dias_laborables_M = Set()
model.dias_laborables_T = Set()
model.dias_laborables_M_cont = Set()
model.dias_laborables_T_cont = Set()
model.horas = Set()
model.dias_horas = Set()
model.mataderos = Set()
model.periodos = Set()
model.mataderos_dia = Set()
model.proveedores_transportista = Set()
model.mataderos_dia_hora = Set()
model.tipo = Set()
model.provincias = Set()
model.fobj = Set()
model.transportistas = Set()

## Define 
#model.primer_dia = Param(default = 'D')
model.numero_transportistas = Param (initialize = 0 )

model.max_transportistas = Param(model.transportistas,default = 100)
model.min_transportistas = Param(model.transportistas,initialize = 0)
model.max_transportistas_horas = Param(model.transportistas,model.horas,default = 100)
model.min_transportistas_horas = Param(model.transportistas,model.horas, default = 0)
model.transportistas_mataderos = Param(model.transportistas, within = Any)
model.fijostp = Param(model.transportistas, initialize = 0)
model.transportistas_provincia1 = Param(model.transportistas, initialize = 0)
model.transportistas_provincia2 = Param(model.transportistas, initialize = 0)
model.long_viaje = Param(model.proveedores, model.mataderos, within = Any)


model.numero_proveedores = Param(  initialize = 0)
model.cargas_noche = Param(model.mataderos_dia, default = 0)
model.proveedores_fijos = Param(model.proveedores, within = Any)
model.cargas_dia = Param(model.proveedores, model.dias,default = 0)
model.cargas = Param(model.proveedores,default = 0)
model.costes = Param(model.proveedores, model.mataderos,default = 0, within = Any)
model.demandas_tipo_md = Param(model.tipo, model.mataderos_dia, default = 0)
model.proveedores_agrupacion = Param(model.proveedores,default = 0)
model.arranque = Param(model.proveedores,default = 0) # toma valor 1 y 0
model.noche = Param(model.proveedores,within=NonNegativeIntegers, default = 0) #toma valores 0,1 y 2
model.provincias_arranques = Param(model.provincias,model.mataderos, default = 0)
model.proveedores_provincias = Param(model.proveedores, default = 0)
model.muylargos = Param(model.proveedores, default = 0)
model.proveedor_municipio = Param(model.proveedores, default = 0)
model.max_cargas_semana = Param(model.proveedores, default = 0)
model.sum_muylargos = Param(  initialize = 0)

#	problem->ndias = 7;
#	problem->nperiod = 2;
#	problem->ndest = 2;
##máximo de carga por proveedor y periodo
P_ut = 3
P_p = 10
#P_max_P = model.numero_proveedores 
#P_max_P = 95


id_prov_Toledo = 48
id_prov_Soria = 45
id_prov_Teruel = 47

#poner un cero o da error al no tener valor


## Define variables
# si se define una variable se tiene que utilizar en otro caso da error
#model.indices = RangeSet(0,1) 
#init_values = {0:0, 1:0}
model.coste = Var(model.fobj, within = NonNegativeReals, initialize = 0 )
#model.coste_total = Var (initialize=0)
model.variables_u = Var(model.proveedores,  within = NonNegativeIntegers, bounds=(0, 4*P_ut),initialize = 0)
model.variables_uidt = Var(model.proveedores, model.dias, model.horas, within = NonNegativeIntegers, bounds=(0, 1),initialize = 0)


model.variables = Var(model.proveedores,model.mataderos_dia_hora, within = NonNegativeReals, initialize =0 )
model.variables_desglosadas = Var(model.proveedores,model.mataderos,model.dias,model.horas, within = NonNegativeIntegers,bounds = (0,2*P_ut), initialize =0 )
#model.demandas = Var(model.tipo,model.mataderos,model.dias, within = NonNegativeIntegers)
model.x_d_t = Var(model.transportistas, model.proveedores,model.mataderos,model.dias,model.horas, within = NonNegativeIntegers,bounds = (0,2*P_ut), initialize =0 )
model.x_pt_mdh = Var (model.proveedores_transportista, model.mataderos_dia_hora, within = NonNegativeIntegers,bounds = (0,2*P_ut), initialize =0 )
# Define Objective Function


## Define Objective Function
def funcion_objetivo(model):
   return (sum(
       model.costes[n,i] * model.variables_desglosadas[n,i,d,h]
       for n in model.proveedores if n <= model.numero_proveedores
       for i in model.mataderos
       for d in model.dias
       for h in model.horas       
    )+ sum( model.variables_u[n]
       for n in model.proveedores if n <= model.numero_proveedores))
model.SolverResult = Objective(rule=funcion_objetivo, sense=minimize)



# Restricciones de igualdad 
# de variables desglosadas
def vinculo_variables(model, n, m):
    i,d2,h = m.split('_') 
    d=int(d2)
    if n <= model.numero_proveedores:
    #  print (i,d,h)
        return model.variables[n,m] == model.variables_desglosadas[n,i,d,h]
    else :
        return Constraint.Skip        
model.igualdad_vars = Constraint(model.proveedores, model.mataderos_dia_hora,rule = vinculo_variables)
 
def rest_coste(model,i):
#   print (i,model.coste[i])
    if i == 1:
        return sum(model.costes[p,m]*model.variables_desglosadas[p,m,d,h]
        for p in model.proveedores if p <= model.numero_proveedores
        for m in model.mataderos
        for d in model.dias
        for h in model.horas) == model.coste[i]
    else:
#    elif:
        return sum( model.variables_u[p]
        for p in model.proveedores if p <= model.numero_proveedores ) == model.coste[i]
        
model.restriccion_coste = Constraint(model.fobj, rule=rest_coste)    
    
 
 
 
#######variables_u_i

# Restricción
def restriccion_rule(model, p, d):
    if p <= model.numero_proveedores:
        return sum(model.variables_desglosadas[p,m,d,t] 
        for m in model.mataderos 
        for t in model.horas) - model.variables_u[p] <= 0
    else :
        return Constraint.Skip
model.restriccion = Constraint(model.proveedores, model.dias, rule=restriccion_rule)


#######

#son las de cada día al menos 
#al menos las que se pidan por demanda del matadero
def constraints3(model, p, d):
 #   print (p, model.cargas[p]) 
 #   print (p,d, model.cargas_dia[p,d])
#    print (1,1,d,model.demanda[1,1,d])
    if p <= model.numero_proveedores:
        if model.cargas_dia[p,d]<99:
            return sum(model.variables_desglosadas[p,m,d,t] 
            for m in model.mataderos 
            for t in model.horas) >= model.cargas_dia[p,d]
        else:
            return sum(model.variables_desglosadas[p,m,d,t] 
            for m in model.mataderos 
            for t in model.horas) == 0
    else :
        return Constraint.Skip   
model.rconstraints3 = Constraint(model.proveedores, model.dias,  rule = constraints3)


#cargas de proveedores
#como mucho lo que pide el proveedor
def igualDemanda2(model,p):
    if p <= model.numero_proveedores:
        return sum(model.variables_desglosadas[p,i,d,h]  
        for i in model.mataderos  
        for d in model.dias 
        for h in model.horas) <= model.cargas[p]
    else :
        return Constraint.Skip
model.demandConstraint2 = Constraint(model.proveedores, rule = igualDemanda2)



##Carga por matadero tipo y día 
##si hay carga debe ser a lo que piden
def mataderotipoydia(model, k, m, d):
    vale=0
#    print (k,k,m,d,model.demandas_tipo_md[k,m+"_"+d]) 
#    if model.demandas_tipo_md[k,m+"_"+d] > 0 and sum(1 for p in model.proveedores if p <= model.numero_proveedores
    if sum(1 for p in model.proveedores if p <= model.numero_proveedores
        for t in model.horas if (model.proveedores_agrupacion[p] == k)) >0:
#       print(k,m,d,"Demanda ",model.demandas_tipo_md[k,m+"_"+str(d)])        
        return sum(model.variables_desglosadas[p,m,d,t] 
        for p in model.proveedores if p <= model.numero_proveedores
        for t in model.horas if (model.proveedores_agrupacion[p] == k)) == model.demandas_tipo_md[k,m+"_"+str(d)]
    else :
        return Constraint.Skip


model.restriccion_Demandas = Constraint(model.tipo,model.mataderos, model.dias, rule=mataderotipoydia)



#######################
####homogeneizar TTS

def restr_Teruel_1(model, d, m):
    if sum(1 for p in model.proveedores    if p <= model.numero_proveedores if model.proveedores_provincias[p] == id_prov_Teruel) >0:
        return sum(model.variables_desglosadas[p,m,d,'N'] - model.variables_desglosadas[p,m,d,'M'] 
        for p in model.proveedores    if p <= model.numero_proveedores if model.proveedores_provincias[p] == id_prov_Teruel) <= 1
    else:    
        return Constraint.Skip
model.restr_Teruel_1 = Constraint(model.dias, model.mataderos, rule=restr_Teruel_1) 

def restr_Teruel_2(model, d, m):
    if sum(1 for p in model.proveedores    if p <= model.numero_proveedores if model.proveedores_provincias[p] == id_prov_Teruel) >0:
        return sum(model.variables_desglosadas[p,m,d,'M'] - model.variables_desglosadas[p,m,d,'N'] 
        for p in model.proveedores if p <= model.numero_proveedores if model.proveedores_provincias[p] == id_prov_Teruel) <= 1
    else:    
        return Constraint.Skip  
   
model.restr_Teruel_2 = Constraint(model.dias, model.mataderos,  rule=restr_Teruel_2)

def restr_Toledo_1(model, d, m):
    if sum(1 for p in model.proveedores    if p <= model.numero_proveedores if model.proveedores_provincias[p] == id_prov_Toledo) >0:
        return sum(model.variables_desglosadas[p,m,d,'N'] - model.variables_desglosadas[p,m,d,'M'] 
        for p in model.proveedores if p <= model.numero_proveedores if model.proveedores_provincias[p] == id_prov_Toledo) <= 1
    else:    
        return Constraint.Skip  
   
model.restr_Toledo_1 = Constraint(model.dias, model.mataderos, rule=restr_Toledo_1) 

def restr_Toledo_2(model, d, m):
    if sum(1 for p in model.proveedores    if p <= model.numero_proveedores if model.proveedores_provincias[p] == id_prov_Toledo) >0:
        return sum(model.variables_desglosadas[p,m,d,'M'] - model.variables_desglosadas[p,m,d,'N'] 
        for p in model.proveedores if p <= model.numero_proveedores if model.proveedores_provincias[p] == id_prov_Toledo) <= 1
    else:    
        return Constraint.Skip     
model.restr_Toledo_2 = Constraint(model.dias, model.mataderos,  rule=restr_Toledo_2)



def restr_Soria_1(model, d, m):
    if sum(1 for p in model.proveedores    if p <= model.numero_proveedores if model.proveedores_provincias[p] == id_prov_Soria) >0:
        return sum(model.variables_desglosadas[p,m,d,'N'] - model.variables_desglosadas[p,m,d,'M'] 
        for p in model.proveedores if p <= model.numero_proveedores if model.proveedores_provincias[p] == id_prov_Soria) <= 1
    else:    
        return Constraint.Skip      

model.restr_Soria_1 = Constraint(model.dias, model.mataderos, rule=restr_Soria_1) 

def restr_Soria_2(model, d, m):
    if sum(1 for p in model.proveedores    if p <= model.numero_proveedores if model.proveedores_provincias[p] == id_prov_Soria) >0:
        return sum(model.variables_desglosadas[p,m,d,'M'] - model.variables_desglosadas[p,m,d,'N'] 
        for p in model.proveedores if p <= model.numero_proveedores if model.proveedores_provincias[p] == id_prov_Soria) <= 1
    else:    
        return Constraint.Skip      
model.restr_Soria_2 = Constraint(model.dias, model.mataderos,  rule=restr_Soria_2)


#################Mañana o Noche

# Restricciones
def restriccion_noche(model, p):
#    print(p,model.noche[p])
    if p <= model.numero_proveedores and model.noche[p] == 1: 
        return sum(model.variables_desglosadas[p,m,d,'M']  for m in model.mataderos for d in model.dias) == 0
    else: 
        return Constraint.Skip           

model.restriccion_noche_2 = Constraint(model.proveedores, rule=restriccion_noche)

def restriccion_manana(model, p):
    if p <= model.numero_proveedores and model.noche[p] == 2:
       return sum(model.variables_desglosadas[p,m,d,'N'] for m in model.mataderos for d in model.dias) == 0
    else: 
        return Constraint.Skip       
       
model.restriccion_manana_2 = Constraint(model.proveedores, rule=restriccion_manana)



#################
#FIJOS

def restriccion_fijos(model, p):
#    print(p,model.noche[p])
    if p <= model.numero_proveedores and model.proveedores_fijos[p] == 'MER':
#        print(p,model.proveedores_fijos[p])
        return sum(model.variables_desglosadas[p,m,d,h] 
        for m in model.mataderos if  m!='M'
        for d in model.dias 
        for h in model.horas) == 0
    elif  p <= model.numero_proveedores and (model.proveedores_fijos[p] == 'TARANCON'  or model.proveedores_fijos[p] == 'TAR'):  
#        print(p,model.proveedores_fijos[p])
        return sum(model.variables_desglosadas[p,m,d,h] 
        for m in model.mataderos if  m!='T'
        for d in model.dias 
        for h in model.horas) == 0
    else:    
        return Constraint.Skip     
        
model.restriccion_fijos= Constraint(model.proveedores, rule=restriccion_fijos)     



########### Hay un máximo a enviar a un matadero en periodo de tiempo por un proveedor

def constraint5(model, p, d, t):
    if model.proveedor_municipio[p] == 1 and p <= model.numero_proveedores: 
        return sum(model.variables_desglosadas[p,m,d,t] for m in model.mataderos) <= P_ut
    else:    
        return Constraint.Skip    
model.restriccion5 = Constraint(model.proveedores, model.dias, model.horas, rule=constraint5)




########### Obligatoriedad de cargas noche y cargas mañana
### Pongo que haya los que me indican por la noche
def constraint_noche(model, m, d, t):
    if t=='N':
        return sum(model.variables_desglosadas[p,m,d,t] for p in model.proveedores if p <= model.numero_proveedores) == model.cargas_noche[m+"_"+str(d)]
    else:    
        return Constraint.Skip  
model.restriccion_noche = Constraint(model.mataderos, model.dias, model.horas, rule=constraint_noche)


###########Dias laborables
def GenerarDiasLaborables(model,d):
    if model.demandas_tipo_md[1,'M'+"_"+str(d)] > 0: 
        model.dias_laborables_M.add(d)         
    if model.demandas_tipo_md[1,'T'+"_"+str(d)] > 0:
        model.dias_laborables_T.add(d)     
    return Constraint.Skip
model.generar_dias_laborables = Constraint(model.dias, rule = GenerarDiasLaborables) 


###########Arranques
def restriccion_arranques_p_T(model,a,d):
    if  model.provincias_arranques[a,'T'] > 0:
        if (d>0 and (((d-1) in  model.dias_laborables_T) == False)or d==0): 
#            print(d,a,'T',model.provincias_arranques[a,'T'])
            return sum(model.variables_desglosadas[p,'T',d,h] 
            for h in model.horas
            for p in model.proveedores if (p <= model.numero_proveedores and model.arranque[p]==1 and model.proveedores_provincias[p]==a)
            ) >= model.provincias_arranques[a,'T']
        else:
            return Constraint.Skip 
    else:
            return Constraint.Skip 
model.restriccion_arranques_p_T = Constraint(model.provincias, model.dias_laborables_T,rule = restriccion_arranques_p_T)

def restriccion_arranques_p_M(model,a,d):
    if  model.provincias_arranques[a,'M'] > 0:
        if (d>0 and (((d-1) in  model.dias_laborables_M) == False)or d==0): 
#            print(d,a,'M',model.provincias_arranques[a,'M'])
            return sum(model.variables_desglosadas[p,'M',d,h] 
            for h in model.horas
            for p in model.proveedores if (p <= model.numero_proveedores and model.arranque[p]==1 and model.proveedores_provincias[p]==a)
            ) >= model.provincias_arranques[a,'M']
        else:
            return Constraint.Skip 
    else:
            return Constraint.Skip 
model.restriccion_arranques_p_M = Constraint(model.provincias, model.dias_laborables_M,rule = restriccion_arranques_p_M)

def MuyLargosTasignacion(model,d,h):
    if model.sum_muylargos>0 and d>0 and (((d-1) in  model.dias_laborables_T) == False) or d==0: 
        return sum(model.variables_desglosadas[p,'T',d,h] for p in model.proveedores if (p <= model.numero_proveedores) and (model.long_viaje[p,'T']=='MUY LARGO')and (model.muylargos[p]==1))==0
    else :
        return Constraint.Skip
model.ConsMuyLargosT= Constraint(model.dias_laborables_T,model.horas,  rule = MuyLargosTasignacion) 

def MuyLargosMasignacion(model,d,h):
    if model.sum_muylargos>0 and d>0 and (((d-1) in  model.dias_laborables_M) == False) or d==0: 
        return sum(model.variables_desglosadas[p,'M',d,h] for p in model.proveedores if (p <= model.numero_proveedores) and (model.long_viaje[p,'M']=='MUY LARGO')and (model.muylargos[p]==1))==0
    else :
        return Constraint.Skip
model.ConsMuyLargosM= Constraint(model.dias_laborables_M,model.horas,  rule = MuyLargosMasignacion) 



########### Restricciones cuando se sabe el municipio de los proveedores

# Active $u_{idt}$ variables.
def AgruparPorMunicipio(model,p,d,h):
    if model.proveedor_municipio[p] == 1: 
        return sum(model.variables_desglosadas[p,m,d,h] for m in model.mataderos)- P_ut*model.variables_uidt[p,d,h] <= 0
    else :
        return Constraint.Skip
model.AgruparPorMunicipio= Constraint(model.proveedores, model.dias, model.horas,  rule = AgruparPorMunicipio) 

# Maximum Loads per Week.
def AgruparPorMunicipio2(model,p):
    if model.proveedor_municipio[p] == 1 and p <= model.numero_proveedores: 
        return  sum(model.variables_uidt[p,d,h]
        for d in model.dias
        for h in model.horas)<= model.max_cargas_semana[p]
    else :
        return Constraint.Skip
model.AgruparPorMunicipio2= Constraint(model.proveedores, rule = AgruparPorMunicipio2) 

# Limit Loads on the Same Day.
def AgruparPorMunicipio3(model,p, d):
    if model.proveedor_municipio[p] == 1 and p <= model.numero_proveedores: 
        return  model.variables_uidt[p,d,'N'] + model.variables_uidt[p,d,'M'] <= 1
    else :
        return Constraint.Skip
model.AgruparPorMunicipio3= Constraint(model.proveedores,model.dias, rule = AgruparPorMunicipio3) 

# Limit Loads on Consecutive Days. 
def AgruparPorMunicipio4(model,p, d):
    if model.proveedor_municipio[p] == 1 and p <= model.numero_proveedores and d+1 in model.dias: 
        return  model.variables_uidt[p,d,'M'] + model.variables_uidt[p,d+1,'N'] <= 1
    else :
        return Constraint.Skip
model.AgruparPorMunicipio4= Constraint(model.proveedores,model.dias, rule = AgruparPorMunicipio4) 