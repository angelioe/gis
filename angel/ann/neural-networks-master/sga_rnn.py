import numpy as np
import matplotlib, random, sqlite3
import matplotlib.pyplot as plt
import jordan as nn_jdn

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

def tune(network,samples):
    pop_size = 1000
    mutate_prob = 0.01
    retain = 0.1
    random_retain = 0.03

    pop = Population(pop_size=pop_size, mutate_prob=mutate_prob, retain=retain, random_retain=random_retain)

    SHOW_PLOT = True
    GENERATIONS = 100
    for x in range(GENERATIONS):
        print ("Generation: ",x)
        pop.grade(network, samples, generation=x)
        pop.evolve(network, samples)
        print ("Best generation individuals:")
        print (pop.best[0].numbers,pop.best[0].fit)
        print (pop.best[1].numbers,pop.best[1].fit)
        if pop.done:
            print("Finished at generation:", x, ", Population fitness:", pop.fitness_history[-1])
            break
    # Plot fitness history
    if SHOW_PLOT:
        print("Showing fitness history graph")
        matplotlib.use("MacOSX")
        plt.plot(np.arange(len(pop.fitness_history)), pop.fitness_history)
        plt.ylabel('Fitness')
        plt.xlabel('Generations')
        plt.title('Fitness - pop_size {} mutate_prob {} retain {} random_retain {}'.format(pop_size, mutate_prob, retain, random_retain))
        plt.show()
    return pop.best[0].numbers

def learn(network,samples, epochs=1000, lrate=.1, momentum=0.1):
    # Train
    for i in range(epochs):
        n = i%samples.size
        network.propagate_forward( samples['input'][n] )
        error = network.propagate_backward( samples['output'][n], lrate, momentum )
        #if (i%5000 == 0):
        #    print("Error:" + str(i) + " - " +str(error))
    # Test
    for i in range(samples.size):
        o = network.propagate_forward( samples['input'][i] )
        #print (i, samples['input'][i], '%.2f' % o[0],'(expected %.2f)' % samples['output'][i])
        forecast = (o == o.max()).astype(float)
        #print ('Sample %d: %s-%s-%s' % (i, cc_sample(samples['input'][i]), cc_sample(samples['output'][i]),cc_sample(forecast)))

    return error

class Individual(object):

    def __init__(self, numbers=None, mutate_prob=0.01):
        if numbers is None:
            self.numbers = np.random.randint(10000, size=2)
        else:
            self.numbers = numbers
            # Mutate
            if mutate_prob > np.random.rand():
                mutate_index = np.random.randint(len(self.numbers) - 1)
                self.numbers[mutate_index] = np.random.randint(10000)

    def fitness(self, network, samples):
        """
            Returns fitness of individual
            Fitness is the difference between
        """
        #target_sum = 4000
        #fit = abs(target_sum - np.sum(self.numbers))
        network.reset()
        sse,mae,rmse,mape=learn(network, samples, 5000, self.numbers[0]/10000, self.numbers[1]/10000)
        self.fit = sse
        #print ("Rate: %s Momentum: %s Final error: %s" % (self.numbers[0]/10000, self.numbers[1]/10000,fit))

        return self.fit

class Population(object):

    def __init__(self, pop_size=2, mutate_prob=0.01, retain=0.2, random_retain=0.03):
        """
            Args
                pop_size: size of population
                fitness_goal: goal that population will be graded against
        """
        self.pop_size = pop_size
        self.mutate_prob = mutate_prob
        self.retain = retain
        self.random_retain = random_retain
        self.fitness_history = []
        self.parents = []
        self.best = []
        self.done = False

        # Create individuals
        self.individuals = []
        for x in range(pop_size):
            self.individuals.append(Individual(numbers=None,mutate_prob=self.mutate_prob))

    def grade(self, network, samples, generation=None):
        """
            Grade the generation by getting the average fitness of its individuals
        """
        fitness_sum = 0
        for x in self.individuals:
            fitness_sum += x.fitness(network, samples)

        pop_fitness = fitness_sum / self.pop_size
        self.fitness_history.append(pop_fitness)
        # Set Done flag if we hit target
        if int(round(pop_fitness*10000)) == 0:
            self.done = True
        # Set Done flag if fitness remains almost the same
        l = len(self.fitness_history)
        if (l>20 and pop_fitness*1.1>=(self.fitness_history[l-2]+self.fitness_history[-3]+self.fitness_history[-4])/3):
            self.done = True

        if generation is not None:
            if generation % 5 == 0:
                print("Episode",generation,"Population fitness:", pop_fitness)

    def select_parents(self, network, samples):
        """
            Select the fittest individuals to be the parents of next generation (lower fitness it better in this case)
            Also select a some random non-fittest individuals to help get us out of local maximums
        """
        # Sort individuals by fitness (we use reversed because in this case lower fintess is better)
        self.individuals = list(reversed(sorted(self.individuals, key=lambda x: x.fit, reverse=True)))
        self.best = self.individuals[:int(4)]
        # Keep the fittest as parents for next gen
        retain_length = self.retain * len(self.individuals)
        self.parents = self.individuals[:int(retain_length)]

        # Randomly select some from unfittest and add to parents array
        unfittest = self.individuals[int(retain_length):]
        for unfit in unfittest:
            if self.random_retain > np.random.rand():
                self.parents.append(unfit)

    def breed(self):
        """
            Crossover the parents to generate children and new generation of individuals
        """
        target_children_size = self.pop_size - len(self.parents)
        children = []
        if len(self.parents) > 0:
            while len(children) < target_children_size:
                father = random.choice(self.parents)
                mother = random.choice(self.parents)
                if father != mother:
                    child_numbers = [ random.choice(pixel_pair) for pixel_pair in zip(father.numbers, mother.numbers)]
                    child = Individual(child_numbers)
                    children.append(child)
            self.individuals = self.parents + children

    def evolve(self, network, samples):
        # 1. Select fittest
        self.select_parents(network, samples)
        # 2. Create children and new generation
        self.breed()
        # 3. Reset parents and children
        self.parents = []
        self.children = []

if __name__ == "__main__":

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
    inputsn = n_cols-1
    outputsn = n_cols-1
    recordsn = n_records
    # -------------------------------- CREATE SAMPLE DATA ---------------------------------------------#
    #inputs=4
    #outputs=4
    #logs=6
    #samples = np.zeros(logs, dtype=[('input',  float, 4), ('output', float, 4)])
    #samples[0]  = (1,0,0,0), (0,1,0,0)
    #samples[1]  = (0,1,0,0), (0,0,1,0)
    #samples[2]  = (0,0,1,0), (0,0,0,1)
    #samples[3]  = (0,0,0,1), (0,0,1,0)
    #samples[4]  = (0,0,1,0), (0,1,0,0)
    #samples[5]  = (0,1,0,0), (1,0,0,0)

    # -------------------------------- CREATE NEURAL NETWORK --------------------------------------------#
    #network = nn_jdn.Jordan(inputs,inputs*2,outputs)
    network = nn_jdn.Jordan(inputsn,(inputsn)*2,outputsn)
    network.reset()
    #error=learn(network, samples)
    #print ("Final error: ",error)
    # ---------------------------------- TUNE NEURAL NETWORK --------------------------------------------#
    best = []
    best = tune (network, samples)
    print (best)
    name = "./lrm/rnn"
    np.save(name, best)
    # ---------------------------------- READ SAVED WEIGHTS --------------------------------------------#
    name = "./lrm/rnn"
    x=np.load(name + '.npy')
    print(x[0],x[1])
