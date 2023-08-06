from __future__ import annotations
from collections.abc import Collection
from dataclasses import dataclass, field
from string import ascii_letters, digits
from random import choice as rand_choice
from typing import ClassVar
from numpy import array, float16, random, zeros
from numpy.typing import NDArray
from pandas import DataFrame
from scipy.signal import find_peaks


@dataclass(frozen=True)
class NeuronTypes:
    """The Izhikevich neuron type containing the behavior variables for the neurons.

    Generates an immutable object containing the behavior variables for the Izhikevich
    equations for the correct function of the neuron.

    Attributes:
        Name (str): The name tag for referring to the NeuronType object.
        a (float): The 'a' value refered on the Izhikevich equations.
        b (float): The 'b' value refered on the Izhikevich equations.
        c (float): The 'c' value refered on the Izhikevich equations.
        d (float): The 'd' value refered on the Izhikevich equations.
    """
    __Name: str = field(default="")
    __a: float = field(default=0.)
    __b: float = field(default=0.)
    __c: float = field(default=0.)
    __d: float = field(default=0.)

    @property
    def Name(self) -> str:
        """The name tag for referring to the NeuronType object."""
        return self.__Name

    @property
    def a(self) -> float:
        """The 'a' value refered on the Izhikevich equations."""
        return self.__a

    @property
    def b(self) -> float:
        """The 'b' value refered on the Izhikevich equations."""
        return self.__b

    @property
    def c(self) -> float:
        """The 'c' value refered on the Izhikevich equations."""
        return self.__c

    @property
    def d(self) -> float:
        """The 'd' value refered on the Izhikevich equations."""
        return self.__d

    @staticmethod
    def __constant_types() -> list[NeuronTypes]:
        """Return a list of dictionaries representing the constant built-in neuron types."""
        return [
            NeuronTypes("Tonic Spiking", 0.02, 0.2, -65, 6),
            NeuronTypes("Phasic Spiking", 0.02, 0.25, -65, 6),
            NeuronTypes("Tonic Bursting", 0.02, 0.2, -50, 2),
            NeuronTypes("Phasic Bursting", 0.02, 0.2, -55, 0.05),
            NeuronTypes("Mixed Mode", 0.02, 0.2, -55, 4),
            NeuronTypes("Spike Frequency Adaptation", 0.01, 0.2, -65, 8),
            NeuronTypes("Class One Excitability", 0.02, -0.1, -55, 6),
            NeuronTypes("Class Two Excitability", 0.2, 0.26, -65, 0),
            NeuronTypes("Spike Lateny", 0.02, 0.2, -65, 6),
            NeuronTypes("Subthreshold Oscilation", 0.05, 0.26, -60, 0),
            NeuronTypes("Resonator", 0.1, 0.26, -60, -1),
            NeuronTypes("Integrator", 0.02, -0.1, -55, 6),
            NeuronTypes("Rebound Spike", 0.03, 0.25, -60, 4),
            NeuronTypes("Rebound Burst", 0.03, 0.25, -52, 0),
            NeuronTypes("Threshold Variability", 0.03, 0.25, -60, 5),
            NeuronTypes("Bistability", 0.1, 0.26, -60, 0),
            NeuronTypes("DAP", 1, 0.2, -60, -21),
            NeuronTypes("Accomodation", 0.02, 1, -55, 4),
            NeuronTypes("Ihibition Induced Spiking", -0.02, -1, -60, 8),
            NeuronTypes("Inhibition Induced Bursting", -0.026, -1, -45, -2)
        ]

    @classmethod
    def from_dict(cls, data: dict[str, str | float]) -> NeuronTypes:
        """Generate a NeuronType object using a dictionary as data model.

        Generate a resulting NeuronType model for an Izhikevich Neuron based
        on a dictionary containing valid keys and data. The data dictionary
        must contain the following keys with their respective types:
            'Name': (str), 'a': (float), 'b': (float), 'c': (float), 'd': (float).

        Args:
            data (dict): A dictionary containing data with only the keys and values as follows:
                'Name': (str), 'a': (float), 'b': (float), 'c': (float), 'd': (float)

        Returns:
            NeuronType: The NeuronTypes object representation containing the dictionary data.

        Raises:
            ValueError: When the data dictionary contains keys different than specified in the
                argument description above.
            TypeError: When the data dictionary contains types different than specified in the
                argument description above."""
        MANDATORY_KEYS = {"Name", "a", "b", "c", "d"}
        # MANDATORY_TYPES = {str, (float, int), (float, int), (float, int), (float, int)}
        incorrect_key: bool = len(MANDATORY_KEYS) != len(data)
        for ref_key, data_key in zip(MANDATORY_KEYS, data.keys()):
            if incorrect_key:
                raise ValueError("The custom type must contain the following keys: {Name, a, b, c, d}.")
            incorrect_key = not (ref_key in data.keys() and data_key in MANDATORY_KEYS)
        # for (data_key, data_value), ref_type in zip(data.items(), MANDATORY_TYPES):
        #    if not isinstance(data_value, ref_type):
        #        raise TypeError(f"The input data for the label {data_key} must be {type(ref_type)}, but is {type(data_value)}")
        return NeuronTypes(str(data["Name"]), float(data["a"]), float(data["b"]), float(data["c"]), float(data["d"]))

    @classmethod
    def get_range(cls, filter: str = "") -> list[NeuronTypes]:
        """Retrieve multiple built-in NeuronTypes based on their names.

        Retrieve a list containing multiple built-in, constant NeuronTypes objects based on common
        keywords in their names. If no argument is provided, a list containing all of the built-in
        NeuronTypes will be retrieved. If the keyword does not match any of Names in the built-in
        NeuronTypes, an empty list will be returned.

        Arguments:
            name(str) optional: The keyword used to filter the built-in NeuronTypes to be retrieved.

        Returns:
            list[NeuronTypes]: The resulting list containing the built-in NeuronTypes objects that
                contain the valid keyword."""
        constant_types = cls.__constant_types()
        if filter == "":
            return constant_types
        result: list[NeuronTypes] = list()
        for data in constant_types:
            if filter.lower() in data.Name.lower():
                result.append(data)
        return result

    @classmethod
    def get_single(cls, name: str) -> NeuronTypes:
        """Retrieve a single built-in NeuronTypes object matching the specified name.

        Retrieve a single built-in NeuronTypes object that matches the specified name given as
        an argument. If none of the built-in NeuronTypes matches the specified name, an empty
        NeuronTypes object will be retrieved.

        Arguments:
            name (str): The search keyword for the specified NeuronTypes to be recovered.

        Returns:
            NeuronTypes: The built-in NeuronTypes object whose name matches the name argument.
        """
        for data in cls.__constant_types():
            if name.lower() == data.Name.lower():
                return data
        return NeuronTypes()

    def as_dict(self) -> dict[str, str | float]:
        """Return the current NeuronTypes object as a dictionary containing its attributes as data.

        Generate a new dictionary object containing the information of the current NeuronTypes object."""
        return {
            "Name": self.__Name,
            "a": self.__a,
            "b": self.__b,
            "c": self.__c,
            "d": self.__d
        }

    def __repr__(self) -> str:
        return f"""Neuron type of name: {self.Name} with properties
        a: {self.a:2f}, b: {self.b:2f}, c: {self.c:2f}, d: {self.d:2f}
        allocated in {hex(id(self))}"""

    def __str__(self) -> str:
        return f"""Neuron type: {self.Name};
        a: {self.a}, b: {self.b}, c: {self.c}, d: {self.d}"""

    def __bool__(self) -> bool:
        data_result = self.__a + self.__b + self.__c + self.__d
        return self.__Name != "" and 0 != data_result

    def __eq__(self, __o: object) -> bool:
        return self.__dict__ == __o.__dict__

    def __ne__(self, __o: object) -> bool:
        return self.__dict__ != __o.__dict__


@dataclass(init=False)
class Neuron:
    """Izhikevich Neuron model for eeg-like simulation.

    The Neuron model based on the Izhikevich equations to determine the voltage response of the Neuron membrane on
    a given time.

    Attributes:
        neuron_type (NeuronTypes): Represents the behavior of the current Neuron object as a NeuronTypes object.
        v0(float | int): Represents the initial voltage value in miliVolts of the current Neuron object.
        is_excitatory(bool): Represents the activity of the current Neuron object, wether it is excitatory or inhibitory.
        tau(float) [global]: Represents the time-step in miliseconds present between each step of the response vector.
            To assign a new value for tau, use the set_tau() method.
        average_white_noise: Represents the average white noise to be added to each point of the response vector.
    """
    __tau: ClassVar[float] = 0.025
    average_white_noise: ClassVar[float] = 1.
    __type: NeuronTypes = field(default_factory=NeuronTypes, init=False)
    __v0: float | int = field(default=-60., init=False)
    __is_excitatory: bool = field(default=True, init=False)

    def __init__(self,
                 v0: float | None = None,
                 n_type: NeuronTypes | None = None,
                 is_excitatory: bool | None = None) -> None:
        self.__v0 = v0 if v0 else -60
        self.__type = n_type if n_type else NeuronTypes.get_single("Tonic Spiking")
        self.__is_excitatory = is_excitatory if is_excitatory else True
        return

    @classmethod
    def tau(self) -> float:
        """Represents the time-step in miliseconds present between each step of the response vector."""
        return self.__tau

    @classmethod
    def set_tau(cls, value: float) -> None:
        """Assign a new global tau value for all the Neuron objects.

        Assign a new global tau value for all the Neuron objects. The given argument must be a positive number
        between 0 and 1.

        Arguments:
            value (float): Represents the newly assigned value for the global tau constant.

        Raises:
            ValueError: When the given argument is out of the interval between 0 and 1 or includes either of the
                limit values."""
        if not (0 < value < 1):
            raise ValueError("The time constant must be decimal value between 0 and 1 without including them!")
        cls.__tau = value
        return

    @property
    def v0(self) -> float:
        """Represents the initial voltage value in miliVolts of the current Neuron object."""
        return float(self.__v0)

    @property
    def is_excitatory(self) -> bool:
        """Represents the activity of the current Neuron object, wether it is excitatory or inhibitory."""
        return self.__is_excitatory

    @property
    def neuron_type(self) -> NeuronTypes:
        """Represents the behavior of the current Neuron object as a NeuronTypes object."""
        return self.__type

    def as_dict(self) -> dict[str, str | float | dict[str, str | float]]:
        """Return a dictionary containing all of the neuron data."""
        return {
            "Type": self.neuron_type.as_dict(),
            "Initial voltage": self.v0,
            "Activity": "Excitatory" if self.__is_excitatory else "Inhibitory",
            "Time constant": self.tau(),
            "Added noise": self.average_white_noise
        }

    def calculate_step(self, V: int | float, u: int | float, I_in: int | float) -> tuple[float, float]:
        """Calculate the next voltage step response for the current Neuron object.

        Compute the next voltage step response for the current given Neuron object using the Izhikevich equations
        and the given data.

        Arguments:
            V(float | int): The current voltage value present in the neuron in miliVolts.
            u(float | int): The current supporting value present in the neuron of the support equation.
            I_in(float | int): The input current value evaluated in nano Ampers.

        Returns:
            tuple[float]: The next iterations of the response voltage and the supporting value with the structure (V, u).
                V(float) -> The next response voltage iteration of the Neuron evaluated in mV.
                u (float) -> The next supporting value iteration for the support Izhikevich equation."""
        if 30 <= V:
            V = float(self.neuron_type.c)
            u += float(self.neuron_type.d)
        V += Neuron.tau() * (0.04 * (V ** 2) + 5 * V + 140 - u + I_in)
        u += Neuron.tau() * float(self.neuron_type.a) * (float(self.neuron_type.b) * V - u)
        V = 30 if 30 <= V else V + self.average_white_noise * random.randn()
        return (V, u)

    def activate(self, T: float | int, I_in: float | int = 0) -> tuple[NDArray[float16], NDArray[float16]]:
        """Generate a pair of vectors with the estimated voltage response over a given period of time and an input current.

        Estimate the neural voltage response in mV and its activations over a given time-period in miliseconds and an input
        current in nano Ampers. Generate a set of responses of the computed activation of the network using the Izhikevich
        equations. Recover the response array and an activations array.

        Arguments:
            T (float | int): The time period to evaluate the Neural response, given as the amount of miliseconds for the evaluation.
            I_in (float | int): The input current to which the Neuron will respond evaluated in nanoAmpers.

        Returns:
            tuple[NDArray]: A tuple of numpy arrays structured as (response_voltage, response_peaks).
                response_voltage(ndarray): The response voltage of the neuron in the given amount of miliseconds T.
                response_peaks(ndarray): The amount of activations the neuron registered in the given amount of miliseconds T.
        """
        vv: list[float] = list()
        v: float = self.v0
        u: float = self.v0 * float(self.neuron_type.b)
        for _ in range(int(T / Neuron.tau())):
            vv.append(v)
            v, u = self.calculate_step(v, u, I_in + random.random())
        peaks, _ = find_peaks(vv, height=20)
        return array(vv, dtype=float16), array(peaks*Neuron.tau(), dtype=float16)

    def __repr__(self) -> str:
        """Return the basic parameters and behavior activity as a string."""
        excitatory_message: str = "Excitatory" if self.__is_excitatory else "Inhibitory"
        return f"""Izhikevich neuron with attributes:
        Type = {self.__type.Name},
        Activity = {excitatory_message},
        Initial voltage = {self.v0} mV
        Allocated in {hex(id(self))}"""

    def __str__(self) -> str:
        return f"""Izhikevich neuron with type: {self.__type.Name}, {"excitatory" if self.__is_excitatory else "inhibitory"}"""

    def __eq__(self, __o: object) -> bool:
        return self.__dict__ == __o.__dict__

    def __ne__(self, __o: object) -> bool:
        return self.__dict__ != __o.__dict__


@dataclass(init=False)
class Network:
    """A community of Neurons evaluated together to simulate a biologic Neural Network.

    A community of Neurons evaluated together to simulate a biologic Neural Network that interacts to different
    stimuli and generates different field responses.

    Attributes:
        neurons(dict[Neuron]): The labeled neurons contained in the current Network object.
        labels(set[str]): The different unique tags used to identify the neurons in the current Network object.
        weights(DataFrame): The matrix representation of the weighted connections representing the interactions
            between each Neuron evaluated in the Network.
        thalamic_ex(float): Represents the thalamic excitation input value to the Network object response.
        thalamic_in(float): Represents the thalamic inhibition input value to the Network object response.
    """
    __neurons: dict[str, Neuron] = field(default_factory=dict, init=False)
    __weights: DataFrame = field(default=DataFrame(), init=False)
    __exc_inp: float = field(default=1, init=False)
    __inh_inp: float = field(default=1, init=False)

    def __random_label(self) -> str:
        """Generate a unique randomized label to fit the Network labels structure and the label collection of the Network."""
        def gen_id() -> str:
            num_digits = len(str(self.total_neurons + 1))
            return "".join(rand_choice(ascii_letters + digits) for _ in range(num_digits))

        new_id = gen_id()
        if 0 < len(self.__neurons):
            while f"n_{new_id}" in set(self.__neurons.keys()):
                new_id = gen_id()
        return f"n_{new_id}"

    @property
    def neurons(self) -> dict[str, Neuron]:
        """The labeled neurons contained in the current Network object"""
        return self.__neurons

    @neurons.setter
    def neurons(self, data: dict[str, Neuron]) -> None:
        if isinstance(data, dict):
            self.__neurons = data
        else:
            raise TypeError("The input data must be a dictionary containing the labeled neurons!")
        self.generate_weights()
        return

    @property
    def total_neurons(self) -> int:
        """The total number of neurons evaluated in the Network."""
        return len(self.__neurons)

    @property
    def weights(self) -> DataFrame:
        """A numerical square matrix representing the weight and connection values of the neurons in the Network."""
        return self.__weights

    @weights.setter
    def weights(self, weights: DataFrame) -> None:
        if not isinstance(weights, DataFrame):
            raise TypeError("Invalid matrix type! The weigths matrix must be set as a pandas DataFrame.")
        if ((weights.select_dtypes(exclude=['number'])).any()).any():
            raise ValueError("Invalid datatype found in the matrix! The matrix must only contain numbers.")
        if (weights.shape != (self.total_neurons, self.total_neurons)):
            raise ValueError("Invalid input! The dimensions of the input weights must be square and "
                             + "equal to the total number of neurons of the network.")
        labels = set(self.neurons.keys())
        self.__weights = DataFrame(weights.to_numpy(), index=labels, columns=labels)
        return

    @property
    def thalamic_ex(self) -> float:
        """Represents the thalamic excitation input value to the Network object response."""
        return float(self.__exc_inp)

    @thalamic_ex.setter
    def thalamic_ex(self, value: float) -> None:
        if 0. >= value:
            raise ValueError("The excitation input value must be a positive number greater than 0!")
        self.__exc_inp = float(value)
        return

    @property
    def thalamic_in(self) -> float:
        """Represents the thalamic inhibition input value to the Network object response."""
        return float(self.__inh_inp)

    @thalamic_in.setter
    def thalamic_in(self, value: float) -> None:
        if 0. >= value:
            raise ValueError("The inhibition input value must be a positive number greater than 0!")
        self.__exc_inp = float(value)
        return

    def add_neurons(self, data: Neuron | dict[str, Neuron] | Collection[Neuron], labels: str | set[str] | None = None) -> None:
        """Append a Neuron or a collection of Neuron objects to the Neuron objects collection in the current Network object.

        Append a Neuron or a collection of Neuron objects to the evaluated Neuron objects in the current Network. Input a single
        Neuron or an iterable collection of Neurons with their labels to add them to the Neuron collection in the Network. The
        labels must be unique and equal to the number of Neurons given in the parameters. If no labels are given, randomized labels
        will be generated for the added Neurons. Once the Neurons and labels have been correctly added to the Network, a new matrix
        of randomized weights is generated to match the new collection of Neurons and labels.

        Arguments:
            data(Neuron | dict[str, Neuron] | Collection[Neuron]): The Neuron(s) to be added to the Network and be evaluated among the
                existent collection of Neurons.
            labels(str | set[str]): The labels assigned to each Neuron entry in the parameter 'data'.

        Raises:
            TypeError: When any of the argument values contain invalid dataTypes.
            ValueError: When the quantities of Neurons and labels do not match with each other.
            ValueError: When a given label is already existent in the Network."""
        if isinstance(data, Neuron):
            new_label = ""
            if labels:
                if not isinstance(labels, str):
                    raise TypeError("When a single neuron is given, the label must be of tipe str!")
                elif labels in self.__neurons.keys():
                    raise ValueError("The given label is already in the Network!")
                else:
                    new_label = str(labels)
            else:
                new_label = self.__random_label()
            self.__neurons[new_label] = data
        elif (isinstance(data, Collection) or issubclass(data, Collection)) and not isinstance(data, dict):
            new_labels = set()
            if labels:
                if not isinstance(labels, set):
                    raise TypeError("When multiple neurons are given, the labels must be given in a set!")
                elif len(labels) != len(data):
                    raise ValueError("The number of labels must match the number of neurons!")
                for n_label in labels:
                    if n_label in self.__neurons.keys():
                        raise ValueError(f"The label {n_label} is already present in the Network!")
                new_labels = labels
            else:
                new_labels = {self.__random_label() for _ in data}
            self.__neurons.update({n_label: n for n_label, n in zip(new_labels, data)})
        elif isinstance(data, dict):
            for label in data.keys():
                if not isinstance(label, str):
                    raise TypeError(f"The label {label} must be a value of type str!")
                elif label in self.__neurons.keys():
                    raise ValueError(f"The label {label} is already present in the Network!")
            self.__neurons.update(data)
        else:
            raise TypeError("The given data must be of type Neuron, a dictionary of labeled neurons or a collection of Neurons!")
        self.generate_weights()
        return

    def generate_weights(self, conn_rate: float = 0.6, exc_cap: int | float = 1, inh_cap: int | float = 1) -> DataFrame:
        """Generate a randomized weight matrix for the current Network object based on the given arguments.

        Generate a weight matrix for the neural network connections and influences for each of the neuron models attached to it.
        The resulting weight matrix will determine the relationship of each neuron with the others.

        Arguments:
            conn_rate(float) [optional]: Sets a threshold for determining if a neuron is connected or not to another neuron, which will
                determine the weight of the influence towards the others. Must be positive between 0 and 1. If it leans towards 0, there will
                be a low connection rate, whereas if it leans towards 1, the connection rate will ben higher.
            exc_cap(int | float) [optional]: Sets a limit for excitatory weights in excitatory connected neurons. Must be positive.
            inh_cap(int | float) [optional]: Sets a limit for inhibitory weights in inhibitory connected neurons. Must be positive.
            labels(list[str]) [optional]: Sets the labels for the neurons contained in the Network, represented in the weight matrix.
                Must be a list containing only strings with a number of elements equal to the total number of neurons.

        Returns:
            DataFrame: A square matrix representing the input weights present in the network."""
        if not (0 < conn_rate < 1):
            raise ValueError("The connection rate must be a positive number between 0 and 1!")
        if 0 >= exc_cap or 0 >= inh_cap:
            raise ValueError("The excitation and inhibition caps must be positive numbers greater than 0!")
        conn_type: NDArray[float16] = array([[(random.random() > (1 - conn_rate))
                                            for _ in range(self.total_neurons)]
                                            for _ in range(self.total_neurons)], dtype=float16)
        weight_type: NDArray[float16] = zeros(array(conn_type).shape, dtype=float16)
        index_labels = list(self.__neurons.keys())
        index_neurons = list(self.__neurons.values())
        for j in range(weight_type.shape[0]):
            for i in range(weight_type.shape[1]):
                if conn_type[j, i] and index_labels[j] != index_labels[i]:
                    weight_type[j, i] = (exc_cap if index_neurons[i].is_excitatory else -inh_cap) * random.random()
        self.__weights = DataFrame(weight_type, index=index_labels, columns=index_labels)
        return self.weights

    def activate(self, T: int, I_in: float = 0, trigger_pos: int = 0, trigger_duration: int = 200,
                 trigger_cap: int | float = 1) -> tuple[NDArray[float16], DataFrame, DataFrame]:
        """Activate the network for a given amount of time evaluated in miliseconds using a trigger neuron response voltage.

        Generate a set of response object representing the computed response over a given time-period presented in miliseconds.
        In order to compute the response, a trigger is generated and computed over a secondary time-period presented as a delay
        to compute the response. The trigger response is injected as an initial value to the specified neuron in the Network.

        Arguments:
            T(int): The period of network response evaluation time represented in miliseconds. Must be positive and greater than 0.
            I_in(float) [optional]: The input current applied to the trigger neuron generated for the network.
            trigger_pos(int) [optional]: The neuron index in the network to which the trigger response is applied.
                Must be within the boundaries of the neurons list in the network.

        Returns:
            tuple[ndarray, DataFrame, DataFrame]: The field response data of the Network activation over the given time-period
                structured as(field_voltage, individual_response, neuron_firings).
                field_voltage(ndarray): A vector containing the sum of all of the individual voltage responses over the given
                    time-period.
                individual_response(DataFrame): A DataFrame containing the individual voltage response for each of the neurons
                    evaluated in the Network over the given time-period.
                neuron_firings(DataFrame): A DataFrame containing the individual firings for each of the neurons evaluated in the
                    Network over the given time-period."""
        # Set the initial values for the run parameters.
        I_net: list[float] = [0. for _ in range(self.total_neurons)]
        v: NDArray[float16] = array([n.v0 for n in self.__neurons.values()])
        u: NDArray[float16] = array([n.v0 * float(n.neuron_type.b) for n in self.__neurons.values()])
        # Prepare the response type structures for the run.
        neuron_firings: dict[str, list[int]] = {n_label: list() for n_label in set(self.neurons.keys())}
        v_individual: dict[str, list[float]] = {n_label: list() for n_label in set(self.neurons.keys())}
        v_field: list[float] = list()   # Prepare an empty list of respones voltage values.
        # Set a trigger neuron response run for the input current with an excitatory neuron.
        trigger_neuron: Neuron = Neuron()
        _, trigger_peaks = trigger_neuron.activate(T=trigger_duration, I_in=I_in)
        I_net[trigger_pos] = trigger_peaks.size * trigger_cap  # Assign the trigger response current to the designated neuron in the network.
        for _ in range(int(T / Neuron.tau())):
            v_field.append(sum(v))
            I_net = [
                self.__exc_inp * random.randn() if n.is_excitatory else self.__inh_inp * random.randn() for n in self.neurons.values()
            ]
            fired = [30 <= v[idx] for idx, _ in enumerate(v)]
            I_net = I_net + [sum(self.weights.to_numpy()[idx, :] * fired) for idx in range(self.total_neurons)]
            for n_idx, (label, neuron) in enumerate(self.__neurons.items()):
                v_individual[label].append(v[n_idx])
                v[n_idx], u[n_idx] = neuron.calculate_step(v[n_idx], u[n_idx], I_net[n_idx])
                neuron_firings[label].append(fired[n_idx])
        return (array(v_field), DataFrame(v_individual), DataFrame(neuron_firings))

    def __init__(
            self,
            neurons: dict[str, Neuron] | list[Neuron] | None = None,
            labels: set[str] | list[str] | None = None,
            weights: DataFrame | None = None,
            exc_inp: float | None = None, inh_inp: float | None = None
    ) -> None:
        self.thalamic_ex = exc_inp if exc_inp else self.__exc_inp
        self.thalamic_in = inh_inp if inh_inp else self.__exc_inp
        if neurons:
            print(f"The input length is {len(neurons)}")
            if isinstance(neurons, dict):
                self.__neurons = neurons if neurons else self.__neurons
            elif isinstance(neurons, list):
                self.__neurons = dict()
                if labels:
                    if len(labels) > len(set(labels)):
                        raise ValueError("The collection of labels must not contain duplicates!")
                    if len(labels) != len(neurons):
                        raise ValueError("The length of labels and neurons does not match!")
                    else:
                        for n_label, neuron in zip(labels, neurons):
                            self.__neurons[n_label] = neuron
                else:
                    for neuron in neurons:
                        self.__neurons[self.__random_label()] = neuron
            self.weights = weights if weights else self.generate_weights()
        else:
            self.__neurons = dict()
        return

    def __repr__(self) -> str:
        """Present the Izhikevich network in the console with its total neurons."""
        message: str = f"""New Izhikevich network with attributes:
        Total neurons = {self.total_neurons}
        Neuron weight matrix = {self.weights.to_string()}
        Allocated at {hex(id(self))}"""
        return message

    def __str__(self) -> str:
        return f"""Izhikevich network with {self.total_neurons} and weight matrix:
        {self.weights.to_string()}"""

    def __len__(self) -> int:
        return self.total_neurons

    def __add__(self, other: Network) -> Network:
        result: Network = Network()
        if isinstance(other, Network):
            result.thalamic_ex = (self.thalamic_ex + other.thalamic_ex)/2
            result.thalamic_in = (self.thalamic_in + other.thalamic_in)/2
            total_neurons = self.neurons
            for n_label, neuron in other.neurons.items():
                new_label = n_label if n_label not in total_neurons.keys() else f"{n_label}_1"
                total_neurons[new_label] = neuron
            result.neurons = total_neurons
        else:
            raise TypeError("A Network can only operate directly with another Network!")
        return result

    def __iadd__(self, other: Network) -> None:
        if isinstance(other, Network):
            self.thalamic_ex = (self.thalamic_ex + other.thalamic_ex)/2
            self.thalamic_in = (self.thalamic_in + other.thalamic_in)/2
            total_neurons = self.neurons
            for n_label, neuron in other.neurons.items():
                new_label = n_label if n_label not in total_neurons.keys() else f"{n_label}_1"
                total_neurons[new_label] = neuron
            self.neurons = total_neurons
        else:
            raise TypeError("A Network can only operate directly with another Network!")
        return

    def __sub__(self, other: Network) -> Network:
        result = Network()
        if isinstance(other, Network):
            result.thalamic_ex = abs(self.thalamic_ex - other.thalamic_ex)*2
            result.thalamic_in = abs(self.thalamic_in - other.thalamic_in)*2
            for n_label, i_neuron in other.neurons.items():
                if n_label in self.neurons and i_neuron == self.neurons[n_label]:
                    self.neurons.pop(n_label)
            result.neurons = self.neurons
        else:
            raise TypeError("A Network can only operate directly with another Network!")
        return result

    def __isub__(self, other: Network) -> None:
        if isinstance(other, Network):
            self.thalamic_ex = abs(self.thalamic_ex - other.thalamic_ex)*2
            self.thalamic_in = abs(self.thalamic_in - other.thalamic_in)*2
            for n_label, i_neuron in other.neurons.items():
                if n_label in self.neurons and i_neuron == self.neurons[n_label]:
                    self.neurons.pop(n_label)
        else:
            raise TypeError("A Network can only operate directly with another Network!")
        return
