from abc import ABC, abstractclassmethod, abstractmethod
from relational_calculus import TupleCalculus as tc

tables = dict()


def add_table_scheme(table_name, table_columns):
    tables[table_name.upper()] = list(
        map(lambda column: str(column).lower(), table_columns))

class DomainCalculus:
    def __init__(self, result, formula) -> None:
        assert isinstance(result, Result) and isinstance(formula, Formula)
        self.result = result
        self.formula = formula
        self.__verify()

    # verify the correctness of the result/formula combination (e.g. one must specify the type of a variable before returning it)
    def __verify(self) -> bool:
        # TODO
        pass

    def to_normal_form(self):
        old_formula = self.formula
        new_formula = self.formula.to_normal_form()
        while new_formula != old_formula:
            old_formula = new_formula
            new_formula = old_formula.to_normal_form()
        return DomainCalculus(self.result, new_formula)

    def __repr__(self) -> str:
        return f'\\{{[{self.result}] \\vert {self.formula}\\}}'

    def to_sql(self) -> str:
        # select statement
        result_query = ''
        for variable in self.result.variables:
            result_query += f'"{variable.name}", '
        result_query = result_query[:-len(', ')]  # remove last ', '

        formula = self.to_normal_form().formula

        # with-as statements and prepare for unions
        # remove exists
        while isinstance(formula, Exists):
            formula = formula.children[0]
        # remove forall
        forall_variables = list()
        while isinstance(formula, Forall):
            forall_variables.append(formula.variable)
            formula = formula.children[0]
        # OR -> UNION: split
        # gather all ORs
        union_formulas = list()
        union_formulas.append(formula)
        while True:
            new_unions = list()
            old_unions = list()
            for formula in union_formulas:
                if isinstance(formula, Or):
                    new_unions.append(formula.children[0])
                    new_unions.append(formula.children[1])
                else:
                    old_unions.append(formula)
            if len(new_unions) == 0:  # no new updates
                break
            union_formulas = list(new_unions + old_unions)

        # AND -> (NATURAL) JOIN
        joins = list()
        for union in union_formulas:
            # gather all tuples
            tuples = list()
            sub_formula = union
            while True:
                if isinstance(sub_formula, And) and isinstance(sub_formula.children[0], Tuple):
                    tuples.append(sub_formula.children[0])
                    sub_formula = sub_formula.children[1]
                elif isinstance(sub_formula, Tuple):
                    tuples.append(sub_formula)
                    sub_formula = None
                else:  # no more Tuples will occur in normal form
                    break
            joins.append((tuples, sub_formula))

        # WITH-AS Statements and SELECTs
        id = 1
        with_query = 'WITH '
        select_queries = []
        for join in joins:
            tuples = join[0]
            sub_formula = join[1]
            select_query = f'SELECT DISTINCT {result_query} '
            from_query = ''
            for t in tuples:
                __quotation_mark = '"' # cannot use backslash in f''-string
                with_query += f'table_{id}({",".join(list(map(lambda var: __quotation_mark + var.name + __quotation_mark, t.variables)))}) AS (SELECT * FROM {t.type}), '
                from_query += f'table_{id} NATURAL JOIN '
                id += 1
            from_query = from_query[:-len(' NATURAL JOIN ')]
            select_query += f'FROM {from_query}'
            if sub_formula is not None:
                # add back the foralls (as 'NOT EXIST ... EXIST NOT sub_formula' to avoid double NOT-NOT's)
                if len(forall_variables) != 0:
                    sub_query = 'NOT EXISTS '
                    for variable in forall_variables:
                        sub_query = f'(SELECT "{variable.name}" FROM {from_query} WHERE EXISTS '
                    sub_query = sub_query[:-len('EXISTS ')]
                    sub_query += f'NOT ({sub_formula.to_sql()})'
                    sub_query += ')' * len(forall_variables)
                else:
                    sub_query = sub_formula.to_sql()
                select_query += f' WHERE {sub_query}'
            select_queries.append(select_query)
        with_query = with_query[:-len(', ')]

        return f'{with_query} {" UNION ".join(select_queries)};'

    def to_tuple_calculus(self) -> tc.TupleCalculus:
        variables_result = set(self.result.variables)
        variables_exists = set()
        variables_forall = set()

        normal_form_formula = self.formula.to_normal_form()

        result_tuples, exists_tuples, forall_tuples = normal_form_formula.get_tuples(
            variables_result, variables_exists, variables_forall)

        #print(f'VARS: {variables_result}')
        #print(f'VARS: {variables_exists}')
        #print(f'VARS: {variables_forall}')

        #print(f'\nTUPLES: {result_tuples}')
        #print(f'TUPLES: {exists_tuples}')
        #print(f'TUPLES: {forall_tuples}')

        # create tc.variables for each dc.tuple
        result_tuples = set(map(lambda t: (t, tc.Variable(type=t.type, name=t.type +
                                                          '_' + ''.join(map(lambda var: str(var.name), t.variables)))), result_tuples))
        exists_tuples = set(map(lambda t: (t, tc.Variable(type=t.type, name=t.type +
                                                          '_' + ''.join(map(lambda var: str(var.name), t.variables)))), exists_tuples))
        forall_tuples = set(map(lambda t: (t, tc.Variable(type=t.type, name=t.type +
                                                          '_' + ''.join(map(lambda var: str(var.name), t.variables)))), forall_tuples))

        #print('')
        #print(f'TUPLES: {result_tuples}')
        #print(f'TUPLES: {exists_tuples}')
        #print(f'TUPLES: {forall_tuples}')

        # reassign the tuples based on where they belong in the formula (result, exists, forall)
        return_tc_vars = dict()
        for value in set(result_tuples):
            dc_tuple = value[0]
            tc_var = value[1]

            in_result = False
            is_forall = False
            for index in range(len(dc_tuple.variables)):
                if not dc_tuple.type in tables.keys() or not len(dc_tuple.variables) == len(tables[dc_tuple.type]):
                    raise Exception(f'The Tuple of type {dc_tuple.type} does not reference a valid Table.')
                var = dc_tuple.variables[index]
                if var in variables_result:
                    in_result = True
                    variables_result.remove(var)
                    column = tables[dc_tuple.type][index]
                    if tc_var in return_tc_vars:
                        attributes = set(return_tc_vars[tc_var])
                        attributes.add(column)
                        return_tc_vars[tc_var] = attributes
                    else:
                        attributes = set()
                        attributes.add(column)
                        return_tc_vars[tc_var] = attributes
                elif var in variables_forall:
                    is_forall = True

            if not in_result:
                if is_forall:
                    result_tuples.remove((dc_tuple, tc_var))
                    forall_tuples.add((dc_tuple, tc_var))
                else:
                    result_tuples.remove((dc_tuple, tc_var))
                    exists_tuples.add((dc_tuple, tc_var))

        #print('')
        #print(f'TUPLES: {result_tuples}')
        #print(f'TUPLES: {exists_tuples}')
        #print(f'TUPLES: {forall_tuples}')

        #print(f'\nRESULT {return_tc_vars}')

        # create a mapping of dc.var to (tc.var, attribute)
        tc_attributes = list()
        for value in set(result_tuples.union(exists_tuples).union(forall_tuples)):
            dc_tuple = value[0]
            tc_var = value[1]

            for index in range(len(dc_tuple.variables)):
                if not dc_tuple.type in tables.keys() or not len(dc_tuple.variables) == len(tables[dc_tuple.type]):
                    raise Exception(f'The Tuple of type {dc_tuple.type} does not reference a valid Table.')
                var = dc_tuple.variables[index]
                column = tables[dc_tuple.type][index]
                tc_attributes.append((var, (tc_var, column)))

        #print(f'\nATTRIBUTES: {tc_attributes}')

        new_formula = normal_form_formula.to_tuple_calculus(tc_attributes)

        #print(f'\nFORMULA:\n{new_formula}')

        # create Equal's between new (variable, attribute) where the old dc_variables were equal
        equals = list()
        for index_1 in range(len(tc_attributes) - 1):
            value_1 = tc_attributes[index_1]
            dc_var_1 = value_1[0]
            tc_var_1 = value_1[1][0]
            tc_column_1 = value_1[1][1]

            for index_2 in range(index_1 + 1, len(tc_attributes)):
                value_2 = tc_attributes[index_2]

                dc_var_2 = value_2[0]
                tc_var_2 = value_2[1][0]
                tc_column_2 = value_2[1][1]

                print(f'EQUALS {dc_var_1} = {dc_var_2}')

                if dc_var_1 == dc_var_2:
                    print(f'EQUALS ADDED {dc_var_1} = {dc_var_2}')
                    equals.append(tc.Equals((tc_var_1, tc_column_1), (tc_var_2, tc_column_2)))

        #print(f'\nEQUALS: {equals}')

        # add equals to the formula
        for equality in equals:
            new_formula = tc.And(equality, new_formula)

        # add forall to formula
        for value in forall_tuples:
            tc_var = value[1]
            new_formula = tc.Forall(tc_var, new_formula)

        # add exists to formula
        for value in exists_tuples:
            tc_var = value[1]
            new_formula = tc.Exists(tc_var, new_formula)

        # add result-tuples to formula
        for value in result_tuples:
            tc_var = value[1]
            new_formula = tc.And(tc_var, new_formula)

        #print(f'\nFORMULA:\n{new_formula}')

        new_result = tc.Result([], return_tc_vars)

        return tc.TupleCalculus(new_result, new_formula)


class Variable:
    def __init__(self, name) -> None:
        assert isinstance(name, str)
        self.name = name.lower()

    def __repr__(self) -> str:
        return f'\\text{{{self.name}}}'


class Result:
    def __init__(self,  variables) -> None:
        assert isinstance(variables, list)
        self.variables = variables

    def __repr__(self) -> str:
        output = ''
        for variable in self.variables:
            output += f'\\text{{{variable.name}}}, '
        output = output[:-2]  # remove last ', '
        return output


class Formula(ABC):
    def __init__(self, children) -> None:
        assert isinstance(children, list)
        self.children = children

    @abstractclassmethod
    def __repr__(self) -> str:
        pass

    @abstractclassmethod
    def __eq__(self, other) -> bool:
        pass

    @abstractclassmethod
    def to_normal_form(self):
        pass

    @abstractclassmethod
    def to_sql(self) -> str:
        pass

    @abstractclassmethod
    def get_tuples(self, variables_result, variables_exist, variables_forall) -> tuple:
        pass

    @abstractclassmethod
    def to_tuple_calculus(self, attributes) -> tc.TupleCalculus:
        pass

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)


class Tuple(Formula):
    new_var_index = 1  # for the conversion of Non-Variables in Tuples to Variables

    def __init__(self, type, variables) -> None:
        assert isinstance(type, str) and isinstance(variables, list)
        super().__init__([])
        self.type = type.upper()
        self.variables = variables

    def __repr__(self) -> str:
        output = f'\\text{{{self.type}}}('
        for variable in self.variables:
            if isinstance(variable, Variable):
                output += f'\\text{{{variable.name}}}, '
            elif isinstance(variable, str):
                output += f'\\text{{"{variable}"}}, '
            else:
                output += f'\\text{{{variable}}}, '

        output = output[:-len(', ')]  # remove last ', '
        output += ')'
        return output

    def __eq__(self, other) -> bool:
        return self.type == other.type and self.variables == other.variables

    def __hash__(self) -> int:
        return hash(tuple((Tuple, self.type, ', '.join(list(map(lambda var: str(var.name), self.variables))))))

    def to_normal_form(self) -> Formula:
        new_variables = list()
        new_tuple = list()
        for var in self.variables:
            if isinstance(var, Variable):
                new_tuple.append(var)
            else:
                new_var = Variable(f'{self.type}_{var}_{Tuple.new_var_index}')
                new_variables.append((new_var, var))
                new_tuple.append(new_var)
                Tuple.new_var_index += 1
        formula = Tuple(self.type, new_tuple)
        for (new_var, old_val) in new_variables:
            formula = Exists(new_var, And(formula, Equals(new_var, old_val)))
        return formula

    def to_sql(self) -> str:
        # will be handled in DomainCalculus.to_sql()
        return None

    def get_tuples(self, variables_result, variables_exist, variables_forall) -> tuple:
        # check if one variable is in list
        is_result = False
        is_forall = False
        for var in self.variables:
            if var in variables_result:
                is_result = True
                continue
            if var in variables_exist:
                continue
            elif var in variables_forall:
                is_forall = True
                continue
            else:
                raise Exception("The input formula's sytax is incorrect.")

        if is_result:
            return (set([self]), set(), set())
        elif is_forall:
            return (set(), set(), set([self]))
        else:
            return (set(), set([self]), set())

    def to_tuple_calculus(self, attributes) -> tc.TupleCalculus:
        return None


class Equals(Formula):
    def __init__(self, left, right) -> None:
        super().__init__([])
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f'{self.left} = {self.right}'

    def __eq__(self, other) -> bool:
        return isinstance(other, Equals) and self.left == other.left and self.right == other.right

    def to_normal_form(self) -> Formula:
        return self

    def to_sql(self) -> str:
        if isinstance(self.left, Variable):
            left_string = f'"{self.left.name}"'
        elif isinstance(self.left, str):
            left_string = f'\'{str(self.left)}\''
        else:
            left_string = f'{str(self.left)}'
        if isinstance(self.right, Variable):
            right_string = f'"{self.right.name}"'
        elif isinstance(self.right, str):
            right_string = f'\'{str(self.right)}\''
        else:
            right_string = f'{str(self.right)}'

        return f'{left_string} = {right_string}'

    def get_tuples(self, variables_result, variables_exist, variables_forall) -> tuple:
        return (set(), set(), set())

    def to_tuple_calculus(self, attributes) -> tc.TupleCalculus:
        new_left = self.left
        if isinstance(self.left, Variable):
            if self.left in dict(attributes).keys():
                new_left = dict(attributes)[self.left]
            else:
                raise Exception('Internal Error')

        new_right = self.right
        if isinstance(self.right, Variable):
            if self.right in dict(attributes).keys():
                new_right = dict(attributes)[self.right]
            else:
                raise Exception('Internal Error')

        return tc.Equals(new_left, new_right)


class GreaterEquals(Formula):
    def __init__(self, left, right) -> None:
        super().__init__([])
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f'{self.left} \\geq {self.right}'

    def __eq__(self, other) -> bool:
        return isinstance(other, GreaterEquals) and self.left == other.left and self.right == other.right

    def to_normal_form(self) -> Formula:
        return self

    def to_sql(self) -> str:
        if isinstance(self.left, Variable):
            left_string = f'"{self.left.name}"'
        else:
            left_string = f'{str(self.left)}'
        if isinstance(self.right, Variable):
            right_string = f'"{self.right.name}"'
        else:
            right_string = f'{str(self.right)}'

        return f'{left_string} >= {right_string}'

    def get_tuples(self, variables_result, variables_exist, variables_forall) -> tuple:
        return (set(), set(), set())

    def to_tuple_calculus(self, attributes) -> tc.TupleCalculus:
        new_left = self.left
        if isinstance(self.left, Variable):
            if self.left in dict(attributes).keys():
                new_left = dict(attributes)[self.left]
            else:
                raise Exception('Internal Error')

        new_right = self.right
        if isinstance(self.right, Variable):
            if self.right in dict(attributes).keys():
                new_right = dict(attributes)[self.right]
            else:
                raise Exception('Internal Error')

        return tc.GreaterEquals(new_left, new_right)


class GreaterThan(Formula):
    def __init__(self, left, right) -> None:
        super().__init__([])
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f'{self.left} > {self.right}'

    def __eq__(self, other) -> bool:
        return isinstance(other, GreaterThan) and self.left == other.left and self.right == other.right

    def to_normal_form(self) -> Formula:
        return self

    def to_sql(self) -> str:
        if isinstance(self.left, Variable):
            left_string = f'"{self.left.name}"'
        else:
            left_string = f'{str(self.left)}'
        if isinstance(self.right, Variable):
            right_string = f'"{self.right.name}"'
        else:
            right_string = f'{str(self.right)}'

        return f'{left_string} > {right_string}'

    def get_tuples(self, variables_result, variables_exist, variables_forall) -> tuple:
        return (set(), set(), set())

    def to_tuple_calculus(self, attributes) -> tc.TupleCalculus:
        new_left = self.left
        if isinstance(self.left, Variable):
            if self.left in dict(attributes).keys():
                new_left = dict(attributes)[self.left]
            else:
                raise Exception('Internal Error')

        new_right = self.right
        if isinstance(self.right, Variable):
            if self.right in dict(attributes).keys():
                new_right = dict(attributes)[self.right]
            else:
                raise Exception('Internal Error')

        return tc.GreaterThan(new_left, new_right)


class LessEquals(Formula):
    def __init__(self, left, right) -> None:
        super().__init__([])
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f'{self.left} \\leq {self.right}'

    def __eq__(self, other) -> bool:
        return isinstance(other, LessEquals) and self.left == other.left and self.right == other.right

    def to_normal_form(self) -> Formula:
        return self

    def to_sql(self) -> str:
        if isinstance(self.left, Variable):
            left_string = f'"{self.left.name}"'
        else:
            left_string = f'{str(self.left)}'
        if isinstance(self.right, Variable):
            right_string = f'"{self.right.name}"'
        else:
            right_string = f'{str(self.right)}'

        return f'{left_string} <= {right_string}'

    def get_tuples(self, variables_result, variables_exist, variables_forall) -> tuple:
        return (set(), set(), set())

    def to_tuple_calculus(self, attributes) -> tc.TupleCalculus:
        new_left = self.left
        if isinstance(self.left, Variable):
            if self.left in dict(attributes).keys():
                new_left = dict(attributes)[self.left]
            else:
                raise Exception('Internal Error')

        new_right = self.right
        if isinstance(self.right, Variable):
            if self.right in dict(attributes).keys():
                new_right = dict(attributes)[self.right]
            else:
                raise Exception('Internal Error')

        return tc.LessEquals(new_left, new_right)


class LessThan(Formula):
    def __init__(self, left, right) -> None:
        super().__init__([])
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f'{self.left} < {self.right}'

    def __eq__(self, other) -> bool:
        return isinstance(other, LessThan) and self.left == other.left and self.right == other.right

    def to_normal_form(self) -> Formula:
        return self

    def to_sql(self) -> str:
        if isinstance(self.left, Variable):
            left_string = f'"{self.left.name}"'
        else:
            left_string = f'{str(self.left)}'
        if isinstance(self.right, Variable):
            right_string = f'"{self.right.name}"'
        else:
            right_string = f'{str(self.right)}'

        return f'{left_string} < {right_string}'

    def get_tuples(self, variables_result, variables_exist, variables_forall) -> tuple:
        return (set(), set(), set())

    def to_tuple_calculus(self, attributes) -> tc.TupleCalculus:
        new_left = self.left
        if isinstance(self.left, Variable):
            if self.left in dict(attributes).keys():
                new_left = dict(attributes)[self.left]
            else:
                raise Exception('Internal Error')

        new_right = self.right
        if isinstance(self.right, Variable):
            if self.right in dict(attributes).keys():
                new_right = dict(attributes)[self.right]
            else:
                raise Exception('Internal Error')

        return tc.LessThan(new_left, new_right)


class Exists(Formula):
    def __init__(self, variable, child) -> None:
        super().__init__([child])
        assert isinstance(variable, Variable)
        self.variable = variable

    def __repr__(self) -> str:
        return f'\\exists_{{\\text{{{self.variable.name}}}}}({self.children[0]})'

    def __eq__(self, other) -> bool:
        return isinstance(other, Exists) and self.variable == other.variable and self.children[0] == other.children[0]

    def to_normal_form(self) -> Formula:
        return Exists(self.variable, self.children[0].to_normal_form())

    def to_sql(self) -> str:
        return None

    def get_tuples(self, variables_result, variables_exist, variables_forall) -> tuple:
        variables_exist.add(self.variable)
        return self.children[0].get_tuples(variables_result, variables_exist, variables_forall)

    def to_tuple_calculus(self, attributes) -> tc.TupleCalculus:
        return self.children[0].to_tuple_calculus(attributes)


class Forall(Formula):
    def __init__(self, variable, child) -> None:
        super().__init__([child])
        assert isinstance(variable, Variable)
        self.variable = variable

    def __repr__(self) -> str:
        return f'\\forall_{{\\text{{{self.variable.name}}}}}({self.children[0]})'

    def __eq__(self, other) -> bool:
        return isinstance(other, Forall) and self.variable == other.variable and self.children[0] == other.children[0]

    def to_normal_form(self) -> Formula:
        if isinstance(self.children[0], Exists):
            return Exists(self.children[0].variable, Forall(self.variable, self.children[0].children[0]).to_normal_form())
        return Forall(self.variable, self.children[0].to_normal_form())

    def to_sql(self) -> str:
        return None

    def get_tuples(self, variables_result, variables_exist, variables_forall) -> tuple:
        variables_forall.add(self.variable)
        return self.children[0].get_tuples(variables_result, variables_exist, variables_forall)

    def to_tuple_calculus(self, attributes) -> tc.TupleCalculus:
        return self.children[0].to_tuple_calculus(attributes)


class And(Formula):
    def __init__(self, child1, child2) -> None:
        super().__init__([child1, child2])

    def __repr__(self) -> str:
        return f'({self.children[0]}\\land {self.children[1]})'

    def __eq__(self, other) -> bool:
        return isinstance(other, And) and self.children[0] == other.children[0] and self.children[1] == other.children[1]

    def to_normal_form(self) -> Formula:
        # check left side first
        if isinstance(self.children[0], Exists):
            return Exists(self.children[0].variable, And(self.children[0].children[0], self.children[1])).to_normal_form()

        if isinstance(self.children[0], Forall):
            return Forall(self.children[0].variable, And(self.children[0].children[0], self.children[1])).to_normal_form()

        if isinstance(self.children[0], Or):  # move Or outward
            return Or(And(self.children[0].children[0], self.children[1]), And(self.children[0].children[1], self.children[1])).to_normal_form()

        if isinstance(self.children[0], And):
            # move Tuple outward
            if isinstance(self.children[0].children[0], Tuple):
                return And(self.children[0].children[0], And(self.children[0].children[1], self.children[1])).to_normal_form()

        # for all other cases of self.children[0] check self.children[1] (right side)
        if isinstance(self.children[1], Exists):
            return Exists(self.children[1].variable, And(self.children[0], self.children[1].children[0]).to_normal_form())

        if isinstance(self.children[1], Forall):
            return Forall(self.children[1].variable, And(self.children[0], self.children[1].children[0])).to_normal_form()

        if isinstance(self.children[1], Or):  # move Or outward
            return Or(And(self.children[0], self.children[1].children[0]), And(self.children[0], self.children[1].children[1])).to_normal_form()

        if isinstance(self.children[1], And):
            # move Tuple outward
            if not isinstance(self.children[0], Tuple) and isinstance(self.children[1].children[0], Tuple):
                return And(self.children[1].children[0], And(self.children[0], self.children[1].children[1])).to_normal_form()

        if isinstance(self.children[1], Tuple):
            # move Tuple left
            if not isinstance(self.children[0], Tuple):
                return And(self.children[1], self.children[0]).to_normal_form()

        # if nothing changed, then convert children
        return And(self.children[0].to_normal_form(), self.children[1].to_normal_form())

    def to_sql(self) -> str:
        return f'({self.children[0].to_sql()} AND {self.children[1].to_sql()})'

    def get_tuples(self, variables_result, variables_exist, variables_forall) -> tuple:
        left_result, left_exists, left_forall = self.children[0].get_tuples(
            variables_result, variables_exist, variables_forall)
        right_result, right_exists, right_forall = self.children[1].get_tuples(
            variables_result, variables_exist, variables_forall)
        return (left_result.union(right_result), left_exists.union(right_exists), left_forall.union(right_forall))

    def to_tuple_calculus(self, attributes) -> tc.TupleCalculus:
        if isinstance(self.children[0], Tuple) and isinstance(self.children[1], Tuple):
            return None
        elif not isinstance(self.children[0], Tuple) and isinstance(self.children[1], Tuple):
            return self.children[0].to_tuple_calculus(attributes)
        elif isinstance(self.children[0], Tuple) and not isinstance(self.children[1], Tuple):
            return self.children[1].to_tuple_calculus(attributes)
        else:
            return tc.And(self.children[0].to_tuple_calculus(attributes),
                          self.children[1].to_tuple_calculus(attributes))


class Or(Formula):
    def __init__(self, child1, child2) -> None:
        super().__init__([child1, child2])

    def __repr__(self) -> str:
        return f'({self.children[0]} \\lor {self.children[1]})'

    def __eq__(self, other) -> bool:
        return isinstance(other, Or) and self.children[0] == other.children[0] and self.children[1] == other.children[1]

    def to_normal_form(self) -> Formula:
        # check left side first
        if isinstance(self.children[0], Exists):
            return Exists(self.children[0].variable, Or(self.children[0].children[0], self.children[1])).to_normal_form()

        if isinstance(self.children[0], Forall):
            return Forall(self.children[0].variable, Or(self.children[0].children[0], self.children[1])).to_normal_form()

        # for all other cases of self.children[0] check self.children[1] (right side)
        if isinstance(self.children[1], Exists):
            return Exists(self.children[1].variable, Or(self.children[0], self.children[1].children[0])).to_normal_form()

        if isinstance(self.children[1], Forall):
            return Forall(self.children[1].variable, Or(self.children[0], self.children[1].children[0])).to_normal_form()

        # if nothing changed, then convert children
        return Or(self.children[0].to_normal_form(), self.children[1].to_normal_form())

    def to_sql(self) -> str:
        return f'({self.children[0].to_sql()} OR {self.children[1].to_sql()})'

    def get_tuples(self, variables_result, variables_exist, variables_forall) -> tuple:
        left_result, left_exists, left_forall = self.children[0].get_tuples(
            variables_result, variables_exist, variables_forall)
        right_result, right_exists, right_forall = self.children[1].get_tuples(
            variables_result, variables_exist, variables_forall)
        return (left_result.union(right_result), left_exists.union(right_exists), left_forall.union(right_forall))

    def to_tuple_calculus(self, attributes) -> tc.TupleCalculus:
        if isinstance(self.children[0], Tuple) and isinstance(self.children[1], Tuple):
            return None
        elif not isinstance(self.children[0], Tuple) and isinstance(self.children[1], Tuple):
            return self.children[0].to_tuple_calculus(attributes)
        elif isinstance(self.children[0], Tuple) and not isinstance(self.children[1], Tuple):
            return self.children[1].to_tuple_calculus(attributes)
        else:
            return tc.Or(self.children[0].to_tuple_calculus(attributes),
                         self.children[1].to_tuple_calculus(attributes))


class Not(Formula):
    def __init__(self, child) -> None:
        super().__init__([child])

    def __repr__(self) -> str:
        return f'\\neg({self.children[0]})'

    def __eq__(self, other) -> bool:
        return isinstance(other, Not) and self.children[0] == other.children[0]

    def to_normal_form(self) -> Formula:
        if isinstance(self.children[0], Not):
            return self.children[0].children[0].to_normal_form()

        if isinstance(self.children[0], And):
            return Or(Not(self.children[0].children[0]), Not(self.children[0].children[1])).to_normal_form()

        if isinstance(self.children[0], Or):
            return And(Not(self.children[0].children[0]), Not(self.children[0].children[1])).to_normal_form()

        if isinstance(self.children[0], Exists):
            return Forall(self.children[0].variable, Not(self.children[0].children[0])).to_normal_form()

        if isinstance(self.children[0], Forall):
            return Exists(self.children[0].variable, Not(self.children[0].children[0])).to_normal_form()

        # if nothing changed, then convert child
        return Not(self.children[0].to_normal_form())

    def to_sql(self) -> str:
        return f'(NOT {self.children[0].to_sql()})'

    def get_tuples(self, variables_result, variables_exist, variables_forall) -> tuple:
        return self.children[0].get_tuples(variables_result, variables_exist, variables_forall)

    def to_tuple_calculus(self, attributes) -> tc.TupleCalculus:
        if isinstance(self.children[0], Tuple):
            return None
        return tc.Not(self.children[0].to_tuple_calculus(attributes))


# temporary test to check the latex output
if __name__ == '__main__':
    print('TESTING \n\n')

    add_table_scheme('Tier', ['ChipID', 'Name', 'Spezies', 'Alter'])
    add_table_scheme('Gehege', ['GehegeNR', 'Sicherheitsstufe', 'AnzahlTiere'])
    add_table_scheme('Tierpfleger', ['MitarbeiterNR', 'Name', 'Berufserfahrung'])
    add_table_scheme('zustaendig', ['MitarbeiterNR', 'GehegeNR', 'ChipID', 'Datum', 'VonUhrzeit', 'BisUhrzeit'])

    MitarbeiterNR = Variable("MitarbeiterNR")
    Name = Variable("Name")
    bE = Variable("bE")
    Alter = Variable("Alter")
    ChipID = Variable("ChipID")
    gNR = Variable("gNR")
    vU1 = Variable("vU1")
    bU1 = Variable("bU1")
    vU2 = Variable("vU2")
    bU2 = Variable("bU2")
    Datum1 = Variable("Datum1")
    Datum2 = Variable("Datum2")

    expression = Exists(bE, Exists(Alter, Exists(ChipID, Exists(gNR, Exists(vU1, Exists(bU1, Exists(vU2, Exists(bU2, Exists(Datum1, Exists(Datum2,
        And(
            Tuple("Tierpfleger", [MitarbeiterNR, Name, bE]),
            And(
                GreaterThan(bE, 4),
                And(
                    Tuple("Tier", [ChipID, "Günther", "Nasenbär", Alter]),
                    And(
                        Tuple("zustaendig", [MitarbeiterNR, gNR, ChipID, Datum1, vU1, bU1]),
                        And(
                            Tuple("zustaendig", [MitarbeiterNR, gNR, ChipID, Datum2, vU2, bU2]),
                            Not(
                                Equals(
                                    Datum1, Datum2
                                )
                            )
                        )
                    )
                )
            )
        )
    ))))))))))

    domainc = DomainCalculus(Result([MitarbeiterNR, Name]), expression)


    print(domainc)
    print(domainc.to_sql())
    print('\n')
    tc = domainc.to_tuple_calculus()
    print(tc)
    print(tc.to_sql())