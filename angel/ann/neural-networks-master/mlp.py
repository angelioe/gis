import numpy as np
import sqlite3, math

def learn(network,samples, epochs=25000, lrate=.5, momentum=0.1):
    # Train
    for i in range(epochs):
        n = np.random.randint(samples.size)
        network.propagate_forward( samples['input'][n] )
        sse,mae,rmse,mape = network.propagate_backward( samples['output'][n], lrate, momentum )
        if (i%5000 == 0):
            print("Error:" + str(i) + " - " +str(sse)+ " - " +str(mae)+ " - " +str(rmse)+ " - " +str(mape))
    # Test
    for i in range(samples.size):
        o = network.propagate_forward( samples['input'][i] )
        print (i, samples['input'][i], '%.2f' % o[0],'(expected %.2f)' % samples['output'][i])

def cc_sample(samplex):
    sample = str(samplex)
    sample = sample.replace("\n","")
    sample = sample.replace(",","")
    sample = sample.replace(" ",".")
    sample = sample.replace("]","")
    sample = sample.replace(")","")
    sample = sample.replace("(","")
    sample = sample.replace("[","")
    return sample

def sigmoid(x):
    ''' Sigmoid like function using tanh '''
    return np.tanh(x)

def dsigmoid(x):
    ''' Derivative of sigmoid above '''
    return 1.0-x**2

class MLP:
    ''' Multi-layer perceptron class. '''

    def __init__(self, *args):
        ''' Initialization of the perceptron with given sizes.  '''

        self.shape = args
        n = len(args)

        # Build layers
        self.layers = []
        # Input layer (+1 unit for bias)
        self.layers.append(np.ones(self.shape[0]+1))
        # Hidden layer(s) + output layer
        for i in range(1,n):
            self.layers.append(np.ones(self.shape[i]))

        # Build weights matrix (randomly between -0.25 and +0.25)
        self.weights = []
        for i in range(n-1):
            self.weights.append(np.zeros((self.layers[i].size,
                                         self.layers[i+1].size)))

        # dw will hold last change in weights (for momentum)
        self.dw = [0,]*len(self.weights)

        # Reset weights
        self.reset()

    def reset(self):
        ''' Reset weights '''

        for i in range(len(self.weights)):
            Z = np.random.random((self.layers[i].size,self.layers[i+1].size))
            self.weights[i][...] = (2*Z-1)*0.25

    def propagate_forward(self, data):
        ''' Propagate data from input layer to output layer. '''

        # Set input layer
        self.layers[0][0:-1] = data

        # Propagate from layer 0 to layer n-1 using sigmoid as activation function
        for i in range(1,len(self.shape)):
            # Propagate activity
            self.layers[i][...] = sigmoid(np.dot(self.layers[i-1],self.weights[i-1]))

        # Return output
        return self.layers[-1]

    def propagate_backward(self, target, lrate=0.1, momentum=0.1):
        ''' Back propagate error related to target using lrate. '''

        deltas = []
        # Errors
        error = target - self.layers[-1]
        sse = ((target - self.layers[-1])**2).sum()
        mae = ((target - self.layers[-1])).sum()/(len((target - self.layers[-1])))
        rmse = math.sqrt(((target - self.layers[-1])**2).sum()/(len((target - self.layers[-1]))))
        mape = ((target - self.layers[-1])/self.layers[-1]).sum()/(len((target - self.layers[-1])))
        # Compute error on output layer
        delta = error*dsigmoid(self.layers[-1])
        deltas.append(delta)
        # Compute error on hidden layers
        for i in range(len(self.shape)-2,0,-1):
            delta = np.dot(deltas[0],self.weights[i].T)*dsigmoid(self.layers[i])
            deltas.insert(0,delta)
        # Update weights
        for i in range(len(self.weights)):
            layer = np.atleast_2d(self.layers[i])
            delta = np.atleast_2d(deltas[i])
            dw = np.dot(layer.T,delta)
            self.weights[i] += lrate*dw + momentum*self.dw[i]
            self.dw[i] = dw

        return sse,mae,rmse,mape

if __name__ == '__main__':

    # -------------------------------- CREATE TRAINING DATA ---------------------------------------------#
    connf = sqlite3.connect('feed.db')
    cf = connf.cursor()
    try: connf.execute('''CREATE TABLE MLP(ID INTEGER PRIMARY KEY);''')
    except: e = "Database already created"
    info = cf.execute("PRAGMA table_info('MLP');")
    cols_mlp=[]
    for i in info:
        cols_mlp.append(i[1])
    n_cols=len(cols_mlp)
    cf.execute("SELECT ID FROM MLP ORDER BY ID DESC LIMIT 1")
    records = cf.fetchone()
    n_records = int(str(records)[1:-2])

    networks=n_cols-7
    inputs=networks-1
    outputs=1
    logs=n_records

    print(cols_mlp)
    print("Networks: ",networks," Inputs: ",inputs," Outputs: ",outputs," Logs: ",logs)

    samples_colx=np.zeros((networks,logs), dtype=[('input',  float, inputs), ('output', float, outputs)])
    for z in range(0,n_cols-7):
        xi = 0
        for x in cols_mlp:
            sqlt="SELECT "+x+" FROM MLP"
            cf.execute(sqlt)
            xdata = cf.fetchall()
            yi = 0
            for y in xdata:
                if(xi<=6):
                    if(str(x)=='ID'):
                        samples_colx[z][yi][0][xi]=float(str(y)[1:-2])
                    elif(str(y)[2:-3]=='x'):
                        samples_colx[z][yi][0][xi]=1.0
                    else:
                        samples_colx[z][yi][0][xi]=float(str(y)[2:-3])
                if (xi > 6):
                    if(xi-7 > z):
                        if(str(y)[2:-3]=='x'):
                            samples_colx[z][yi][0][xi-8]=1.0
                        else:
                            samples_colx[z][yi][0][xi-8]=float(str(y)[2:-3])
                    if(xi-7 < z):
                        if(str(y)[2:-3]=='x'):
                            samples_colx[z][yi][0][xi-7]=1.0
                        else:
                            samples_colx[z][yi][0][xi-7]=float(str(y)[2:-3])
                    if(xi-7 == z):
                        if(str(y)[2:-3]=='x'):
                           samples_colx[z][yi][1]=1.0
                        else:
                          samples_colx[z][yi][1]=float(str(y)[2:-3])
                yi += 1
            xi+=1
    # -------------------------------- CREATE NEURAL NETWORK --------------------------------------------#
    network = MLP(inputs,inputs,outputs)
    # -------------------------- READ LEARNING RATE AND MOMENTUM WEIGHTS --------------------------------#
    #name = "./lrm/mlp"
    #x=np.load(name + '.npy')
    epochs = 25000
    lrate = 0.5
    #lrate=x[0]/10000
    momentum = 0.1
    #momentum=x[1]/10000
    # ---------------------------------- TUNE NEURAL NETWORK --------------------------------------------#
    for n in range(0,networks):
        print ("Learning the ",n," output")
        network.reset()
        learn(network, samples_colx[n], epochs, lrate, momentum)
        name = "./weights/mlp_"+str(n)
        np.save(name, network.weights)
    # ---------------------------------- READ SAVED WEIGHTS --------------------------------------------#
    for n in range(0,networks):
        name = "./weights/mlp_"+str(n)
        x=np.load(name + '.npy')
        #print(x)
