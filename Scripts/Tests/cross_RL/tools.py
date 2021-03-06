# Tools
####################################
import os, sys
import random
import numpy as np
import xml.etree.ElementTree as ET

def get_output_folder(output_dir, exp_id, args_description):
    """Return save folder parent_dir/Results/exp_id

    If this directory already exists it creates parent_dir/Results/exp_id_{i},
    being i the next smallest free number.

    Inside this directory it also creates a sub-directory called model_checkpoints to
    store intermediate training steps.

    This is just convenient so that if you run the
    same script multiple times tensorboard can plot all of the results
    on the same plots with different names.

    Parameters
    ----------
    parent_dir : str
        Path of the directory where results will be stored.

    Returns
    -------
    parent_dir/Results/exp_id
        Path to this run's save directory.
    """
    try:
        # Returns an error if parent_dir already exists
        os.makedirs(output_dir)
    except:
        pass

    exp_run = 1
    if exp_id in os.listdir(output_dir):

        new_folder = os.path.join(output_dir,exp_id,"run"+"_"+str(exp_run))

        while os.path.exists(new_folder):
            exp_run +=1
            new_folder = os.path.join(output_dir,exp_id,"run"+"_"+str(exp_run))

        output_dir = new_folder
        os.makedirs(output_dir)
        os.mkdir(os.path.join(output_dir,"model_checkpoints"))
        summary_writer_folder = os.path.join(output_dir,args_description)
        os.mkdir(summary_writer_folder)
    else:
        output_dir = os.path.join(output_dir,exp_id,"run"+"_"+str(exp_run))
        os.makedirs(output_dir)
        os.mkdir(os.path.join(output_dir,"model_checkpoints"))
        summary_writer_folder = os.path.join(output_dir,args_description)
        os.mkdir(summary_writer_folder)


    return output_dir , summary_writer_folder


### TO DO
# Create a class to specify different types of demand


def get_veh_sec(x, demand,high, nominal,total_time):

    if demand == "rush":
        part = total_time/5
        if x < part:
            return np.random.normal(nominal, nominal/10)
        if x < 2*part:
            aux = (nominal-high)/(-part)*x + nominal + (nominal-high)
            return np.random.normal(aux, aux/10)
        if x < 3*part:
            return high
        if x < 4*part:
            aux = -(high-nominal)/(part)*x + high+(high-nominal)*3
            return np.random.normal(aux, aux/10)
        else:
            return np.random.normal(nominal, nominal/10)
    else:
        return 1

def generate_routefile(route_file_dir, demand):
    """Returns XML file specifying network layout for sumo simulation"""

    N = 3600  # number of time steps

    nominal = 1
    high =2 # At rush hour two times more cars

    # demand per second from different directions

    pEW = 1 / 20
    pNS = 1 / 80
    pWE = 1 / 20
    pSN = 1 / 80

    with open(route_file_dir, "w") as routes:
        print("""<routes>
        <vType id="car" accel="0.8" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" guiShape="passenger"/>
        <route id="right" edges="51o 1i 2o 52i" />
        <route id="left" edges="52o 2i 1o 51i" />
        <route id="down" edges="54o 4i 3o 53i" />
        <route id="up" edges="53o 3i 4o 54i" />""", file=routes)
        vehNr = 0

        for i in range(N):
            if random.uniform(0, 1) < pWE*get_veh_sec(i,demand,high,nominal,N):
                print('    <vehicle id="right_%i" type="car" route="right" depart="%i" />' % (
                    vehNr, i), file=routes)
                vehNr += 1
            if random.uniform(0, 1) < pEW*get_veh_sec(i,demand,high,nominal,N):
                print('    <vehicle id="left_%i" type="car" route="left" depart="%i" />' % (
                    vehNr, i), file=routes)
                vehNr += 1
            if random.uniform(0, 1) < pNS*get_veh_sec(i,demand,high,nominal,N):
                print('    <vehicle id="down_%i" type="car" route="up" depart="%i" color="1,0,0"/>' % (
                    vehNr, i), file=routes)
                vehNr += 1
            if random.uniform(0, 1) < pSN*get_veh_sec(i,demand,high,nominal,N):
                print('    <vehicle id="UP_%i" type="car" route="down" depart="%i" color="1,0,0"/>' % (
                    vehNr, i), file=routes)
                vehNr += 1
        print("</routes>", file=routes)


def get_vehicle_delay(output_dir):

    tree = ET.parse(os.path.join(output_dir,'tripinfo.xml'))
    root = tree.getroot()

    vehicle_delay = []

    for veh in root:
        vehicle_delay.append(float(veh.get("duration")))

    return vehicle_delay
