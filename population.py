import os
import sys
from datetime import *
import pickle

# For use in contexts where this file is imported from outside this directory.
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

from species import *
from neural_network import *

class Population:

    def __init__(self, num_inputs, num_outputs, initial_num_hidden_nodes=0, max_num_hidden_nodes=default_max_num_hidden_nodes, output_activation_function=default_output_activation_function, mode="unconnected", population_size=default_population_size, num_initial_mutations=1, num_generations=None, output_stream_name="sys.stdout"):

        self.population_size = population_size
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs
        self.initial_num_hidden_nodes = initial_num_hidden_nodes
        self.max_num_hidden_nodes = max_num_hidden_nodes
        self.output_activation_function = output_activation_function
        self.num_initial_mutations = num_initial_mutations
        self.num_generations = num_generations

        self.output_stream_name = output_stream_name
        self.output_stream = eval(self.output_stream_name)

        self.mode = mode

        self.fitness_goal = None
        self.generation = 0

        self.genomes = None
        self.species = None
        self.misfits = None
        self.neural_networks = None

        self.champion = None
        self.generation_champion = None
        self.generation_start_time = None
        self.generation_end_time = None

        self.genome_fitnesses = None

        self.initialize()
        self.initial_mutation()
        self.set_species()
        self.set_neural_networks()

    def initialize(self):

        self.genomes = []
        self.species = []
        self.misfits = []
        self.neural_networks = []

        self.genome_fitnesses = []

        for i in range(self.population_size):

            self.misfits.append(
                Genome.default(num_inputs=self.num_inputs,
                               num_outputs=self.num_outputs,
                               num_hidden_nodes=self.initial_num_hidden_nodes,
                               max_num_hidden_nodes=self.max_num_hidden_nodes,
                               output_activation_function=self.output_activation_function)
            )

        self.generation = 1

    def initial_mutation(self):

        for i in range(self.num_initial_mutations):
            for genome in self.misfits:
                genome.random_mutation()

    def run(self, evaluation_function, num_generations=None, fitness_goal=None):

        if num_generations is None and fitness_goal is None:
            num_generations = self.num_generations
        elif fitness_goal is not None:
            self.fitness_goal = fitness_goal
        assert not (num_generations is None and fitness_goal is None)

        while (num_generations is None or self.generation <= num_generations) and (fitness_goal is None or (self.champion is None or self.champion.fitness < fitness_goal)):

            # Stuff to do before evaluation.
            self.pre_evaluation_tasks()

            # Evaluate here.
            for neural_network in self.neural_networks:
                neural_network.genome.fitness = evaluation_function(neural_network)

            # Stuff to do after evaluation.
            self.post_evaluation_tasks()

        return self.champion

    def run_skeleton(self, evaluation_function, num_generations=None, fitness_goal=None):

        while( self.continue_run(num_generations=num_generations, fitness_goal=fitness_goal) ):

            self.pre_evaluation_tasks()

            for neural_network in self.neural_networks:
                neural_network.genome.fitness = evaluation_function(neural_network)

            self.post_evaluation_tasks()

        return self.champion

    def pre_evaluation_tasks(self):

        if self.output_stream is not None:
            print("Beginning generation {} with {} individuals of {} species.".format(self.generation, len(self.genomes), len(self.species)), file=self.output_stream)

        self.generation_start_time = datetime.now()

    def post_evaluation_tasks(self):

        self.genome_fitnesses += [[genome.fitness for genome in self.genomes]]

        self.set_champions()

        for species in self.species:
            species.step_generation()

        self.generation_end_time = datetime.now()

        if self.output_stream is not None:
            self.report_generation()

        self.remove_stagnated_species()
        self.reproduce()
        self.transfer_offspring()

        self.set_species()
        self.remove_extinct_species()

        self.set_neural_networks()

        self.champion.save("champion.genome")

        self.generation += 1

        return self.champion, self.generation_champion

    def continue_run(self, num_generations=None, fitness_goal=None):

        if num_generations is None and fitness_goal is None:
            num_generations = self.num_generations
        elif fitness_goal is not None:
            self.fitness_goal = fitness_goal
        assert not (num_generations is None and fitness_goal is None)

        return (num_generations is None or self.generation <= num_generations) and (fitness_goal is None or (self.champion is None or self.champion.fitness < fitness_goal))

    def set_neural_networks(self):

        self.neural_networks.clear()
        for genome in self.genomes:
            self.neural_networks.append( FeedForwardNeuralNetwork(genome) )

    def report_generation(self):

        for i in range(65):
            print("-", end="", file=self.output_stream)
        print(file=self.output_stream)
        print("%-6s%5s%10s%15s%15s%13s" % ("Species", "Age", "Members", "Best Fitness", "Ave Fitness", "Std Dev"),
              file=self.output_stream)
        for i in range(65):
            print("-", end="", file=self.output_stream)
        print(file=self.output_stream)
        for species in self.species:
            print(species.information_entry(), file=self.output_stream)

        print("Best genome in generation {}: genome {}, fitness: {}".format(self.generation, self.generation_champion.identifier, round(self.generation_champion.fitness, 2)), file=self.output_stream, end="\n")
        print("Best genome so far: {}, fitness: {}".format(self.champion.identifier, round(self.champion.fitness, 2)),
              end="")
        if self.fitness_goal is not None:
            print(" ({}% of {} goal)".format(round(100 * float(self.champion.fitness) / self.fitness_goal, 2), self.fitness_goal), file=self.output_stream)
        else:
            print()
        print("Processing time for generation {}: {}s".format(self.generation, round((self.generation_end_time - self.generation_start_time).total_seconds(), 2)), end="\n\n", file=self.output_stream)

    def reproduce(self):

        self.set_total_fitness()

        self.species.sort(key=lambda species : species.fitness, reverse=True)

        if exact_population_size:

            num_children = {}
            for species in self.species:
                num_children.update( {species : int(round((self.population_size * species.average_fitness() / self.total_fitness), 0)) } )

            # correct potential error in number of children requested
            raw_num_children = sum(num_children.values())
            error = raw_num_children - self.population_size
            delta = 0
            if error > 0:
                delta = -1
            elif error < 0:
                delta = 1

            while error is not 0:
                max_num_children = max(num_children[species] for species in self.species)
                most_populated_species = [species for species in self.species if num_children[species] is max_num_children]
                most_populated_species.sort(key=lambda species : species.fitness)

                for i in range(min(abs(error), len(most_populated_species))):
                    species = most_populated_species[i]
                    num_children[species] += delta
                    error += delta
            assert sum(num_children.values()) == 150, "Number of children requested: {}.".format(sum(num_children.values()))

            for species in self.species:
                species.reproduce(num_children[species])

        else:
            for species in self.species:
                num_children = int(round((self.population_size * species.average_fitness() / self.total_fitness), 0))
                species.reproduce(num_children)

    def transfer_offspring(self):

        self.genomes.clear()
        self.misfits.clear()
        for species in self.species:

            self.genomes += species.genomes
            self.misfits += species.misfits

    def set_champions(self):

        self.genomes.sort(key = lambda genome : genome.fitness, reverse = True)

        self.generation_champion = deepcopy(self.genomes[0])
        if self.champion is None or self.generation_champion.fitness > self.champion.fitness:
            self.champion = self.generation_champion

    # This function may be better with a different method for finding compatible species that ranks them by similarity
    def set_species(self):

        for genome in self.misfits:

            compatible_species = ([species for species in self.species if species.is_compatible_with(genome)] + [None])[0]
            if compatible_species is None:
                new_species = Species(genome=genome, current_generation=self.generation)
                self.species.append(new_species)

            else:
                compatible_species.add_genome(genome)

            self.genomes.append(genome)

        self.misfits.clear()

    def set_total_fitness(self):

        total_fitness = sum([species.average_fitness() for species in self.species])
        if total_fitness == 0:
            total_fitness = 1

        self.total_fitness = total_fitness

        return total_fitness

    def remove_stagnated_species(self):

        stagnated_species = [species for species in self.species if species.is_stagnated()]
        for species in stagnated_species:
            if self.output_stream is not None:
                print("Removing stagnated species {}.".format(species.identifier), file=self.output_stream)
            self.species.remove(species)
        if len(stagnated_species) > 0 and self.output_stream is not None:
            print(file=self.output_stream)

    def remove_extinct_species(self):

        extinct_species = [species for species in self.species if species.is_extinct()]
        for species in extinct_species:
            if self.output_stream is not None:
                print("Removing extinct species {}.".format(species.identifier), file=self.output_stream)
            self.species.remove(species)
        if len(extinct_species) > 0 and self.output_stream is not None:
            print(file=self.output_stream)

    def size(self):

        return len(self.genomes) + len(self.misfits)

    def num_species(self):

        return len(self.species)

    def save(self, filename):

        # Output streams are not serializable.

        self.output_stream = self.output_stream_name

        file = open(filename, "wb")
        pickle.dump(self, file, protocol=1)
        file.close()

        self.output_stream = eval(self.output_stream_name)

    @classmethod
    def from_file(cls, filename):

        file = open(filename, "rb")
        population = pickle.load(file)
        file.close()
        
        population.output_stream = eval(population.output_stream)
        return population

    def save_run_data(self, filename="population_{}_gen{}.data"):

        file = open(filename, "wb")
        pickle.dump(self.genome_fitnesses, file, protocol=1)
        file.close()

    @classmethod
    def load_run_data(cls, filename):

        file = open(filename, "rb")
        run_data = pickle.load(file)
        file.close()

        return run_data

    def __str__(self):

        return "Population of {} individuals in {} species. {} inputs, {} outputs.".format(self.size(), self.num_species(),  self.num_inputs, self.num_outputs)