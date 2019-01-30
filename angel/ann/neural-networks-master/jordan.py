import numpy as np
import sqlite3, math

def learn(network,samples, epochs=100000, lrate=.0001, momentum=0.15):
    # Train
    for i in range(epochs):
        n = i%samples.size
        network.propagate_forward( samples['input'][n] )
        sse,mae,rmse,mape = network.propagate_backward( samples['output'][n], lrate, momentum )
        if (i%5000 == 0):
            print("Error:" + str(i) + " - " +str(sse)+ " - " +str(mae)+ " - " +str(rmse)+ " - " +str(mape))
    # Test
    for i in range(samples.size):
        o = network.propagate_forward( samples['input'][i] )
        #print (i, samples['input'][i], '%.2f' % o[0],'(expected %.2f)' % samples['output'][i])
        forecast = (o == o.max()).astype(float)
        print ('Sample %d: %s-%s-%s' % (i, cc_sample(samples['input'][i]), cc_sample(samples['output'][i]),cc_sample(forecast)))

def cc_sample(samplex):
    sample = str(samplex)
    sample = sample.replace("\n","")
    sample = sample.replace(",","")
    sample = sample.replace(".","")
    sample = sample.replace(" ","")
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

class Jordan:
    ''' Jordan network '''
    def __init__(self, *args):
        ''' Initialization of the perceptron with given sizes.  '''
        self.shape = args
        n = len(args)
        # Build layers
        self.layers = []
        # Input layer (+1 unit for bias
        #              +size of oputput layer)
        self.layers.append(np.ones(self.shape[0]+1+self.shape[-1]))
        # Hidden layer(s) + output layer
        for i in range(1,n):
            self.layers.append(np.ones(self.shape[i]))
        # Build weights matrix (randomly between -0.25 and +0.25)
        self.weights = []
        for i in range(n-1):
            self.weights.append(np.zeros((self.layers[i].size, self.layers[i+1].size)))
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
        # Set input layer with data
        self.layers[0][0:self.shape[0]] = data
        # and output layer
        self.layers[0][self.shape[0]:-1] = self.layers[-1]
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
        # Return error
        return sse,mae,rmse,mape

if __name__ == '__main__':

    # -------------------------------- CREATE TRAINING DATA ---------------------------------------------#
    connf = sqlite3.connect('feed.db')
    cf = connf.cursor()
    try: connf.execute('''CREATE TABLE RNN(ID INTEGER PRIMARY KEY);''')
    except: e = "Database already created"
    info = cf.execute("PRAGMA table_info('RNN');")
    cols_rnn=[]
    for i in info:
        cols_rnn.append(i[1])
    n_cols=len(cols_rnn)
    cf.execute("SELECT ID FROM RNN ORDER BY ID DESC LIMIT 1")
    records = cf.fetchone()
    n_records = int(str(records)[1:-2])
    samples_rnn = np.zeros(n_records, dtype=[('input',  float, n_cols), ('output', float, n_cols)])
    xi = 0
    yi = 0
    for x in cols_rnn:
        sqlt="SELECT "+x+" FROM RNN"
        cf.execute(sqlt)
        xdata = cf.fetchall()
        yi = 0
        for y in xdata:
            if (str(y)[1:-2] == 'None'):
                samples_rnn[yi][0][xi]=0
            elif (str(y)[2:-3] == '1'):
                samples_rnn[yi][0][xi]=1
            elif (str(y)[2:-3] == '0'):
                samples_rnn[yi][0][xi]=0
            else:
                samples_rnn[yi][0][xi]=int(str(y)[1:-2])
            yi += 1
        xi+=1
    for x in range(0,len(samples_rnn)):
        if (x<n_records-1):
            samples_rnn[x][1]=samples_rnn[x+1][0]
        if (x==n_records-1):
            samples_rnn[x][1]=samples_rnn[0][0]

    samples_train = np.zeros(n_records, dtype=[('input',  float, n_cols-1), ('output', float, n_cols-1)])
    for l in range (0,n_records):
        for k in range (1,n_cols):
            samples_train[l][0][k-1]=samples_rnn[l][0][k]
            samples_train[l][1][k-1]=samples_rnn[l][1][k]
        #print(cc_sample(samples_train[l][0]),cc_sample(samples_train[l][1]))
    samples = samples_train
    # -------------------------------- CREATE NEURAL NETWORK --------------------------------------------#
    inputsn = n_cols-1
    outputsn = n_cols-1
    recordsn = n_records
    network = Jordan(inputsn,(inputsn)*2,outputsn)
    # -------------------------- READ LEARNING RATE AND MOMENTUM WEIGHTS --------------------------------#
    #name = "./lrm/rnn"
    #x=np.load(name + '.npy')
    epochs = 100000
    lrate = 0.0001
    #lrate=x[0]/10000
    momentum = 0.15
    #momentum=x[1]/10000
    # ---------------------------------- TUNE NEURAL NETWORK --------------------------------------------#
    network.reset()
    learn(network, samples, epochs, lrate, momentum)
    name = "./weights/rnn"
    np.save(name, network.weights)
    # ---------------------------------- READ SAVED WEIGHTS --------------------------------------------#
    name = "./weights/rnn"
    x=np.load(name + '.npy')
    #print(x)
