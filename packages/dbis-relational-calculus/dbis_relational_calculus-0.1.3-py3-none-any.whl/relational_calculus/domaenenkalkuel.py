from abc import ABC, abstractclassmethod, abstractmethod


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
            result_query += f'{variable.name}, '
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
            tmp = list()
            for formula in union_formulas:
                if isinstance(formula, Or):
                    tmp.append(formula.children[0])
                    tmp.append(formula.children[1])
            if len(tmp) == 0:  # no new updates
                break
            union_formulas = list(tmp)

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
            select_query = f'SELECT {result_query} '
            from_query = ''
            for t in tuples:
                with_query += f'table_{id}({",".join(list(map(lambda var: var.name, t.variables)))}) AS (SELECT * FROM {t.type}), '
                from_query += f'table_{id} NATURAL JOIN '
                id += 1
            from_query = from_query[:-len(' NATURAL JOIN ')]
            select_query += f'FROM {from_query}'
            if sub_formula is not None:
                # add back the foralls (as 'NOT EXIST ... EXIST NOT sub_formula' to avoid double NOT-NOT's)
                if len(forall_variables) != 0:
                    sub_query = 'NOT EXISTS '
                    for variable in forall_variables:
                        sub_query = f'(SELECT {variable.name} FROM {from_query} WHERE EXISTS '
                    sub_query = sub_query[:-len('EXISTS ')]
                    sub_query += f'NOT ({sub_formula.to_sql()})'
                    sub_query += ')' * len(forall_variables)
                else:
                    sub_query = sub_formula.to_sql()
                select_query += f' WHERE {sub_query}'
            select_queries.append(select_query)
        with_query = with_query[:-len(', ')]

        return f'{with_query} {" UNION ".join(select_queries)};'


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

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)


class Tuple(Formula):
    new_var_index = 1  # for the conversion of Non-Variables in Tuples to Variables

    def __init__(self, type, variables) -> None:
        assert isinstance(type, str) and isinstance(variables, list)
        super().__init__([])
        self.type = type
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
            left_string = f'{self.left.name}'
        elif isinstance(self.left, str):
            left_string = f'\'{str(self.left)}\''
        else:
            left_string = f'{str(self.left)}'
        if isinstance(self.right, Variable):
            right_string = f'{self.right.name}'
        elif isinstance(self.right, str):
            right_string = f'\'{str(self.right)}\''
        else:
            right_string = f'{str(self.right)}'

        return f'{left_string} = {right_string}'


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
            left_string = f'{self.left.name}'
        else:
            left_string = f'{str(self.left)}'
        if isinstance(self.right, Variable):
            right_string = f'{self.right.name}'
        else:
            right_string = f'{str(self.right)}'

        return f'{left_string} >= {right_string}'


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
            left_string = f'{self.left.name}'
        else:
            left_string = f'{str(self.left)}'
        if isinstance(self.right, Variable):
            right_string = f'{self.right.name}'
        else:
            right_string = f'{str(self.right)}'

        return f'{left_string} > {right_string}'


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
            left_string = f'{self.left.name}'
        else:
            left_string = f'{str(self.left)}'
        if isinstance(self.right, Variable):
            right_string = f'{self.right.name}'
        else:
            right_string = f'{str(self.right)}'

        return f'{left_string} <= {right_string}'


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
            left_string = f'{self.left.name}'
        else:
            left_string = f'{str(self.left)}'
        if isinstance(self.right, Variable):
            right_string = f'{self.right.name}'
        else:
            right_string = f'{str(self.right)}'

        return f'{left_string} < {right_string}'


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


class Not(Formula):
    def __init__(self, child) -> None:
        super().__init__([child])
        # not supported, since it doesn't make any sense
        assert not isinstance(child, Tuple)

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


# temporary test to check the latex output
if __name__ == '__main__':
    t = Variable(name='tk')
    x = Variable('x')
    y = Variable('y')
    z = Variable('z')

    eq = Equals('5', t)
    print(eq)

    tuple1 = Tuple('HAUPTSTADT', [t, z])
    tuple2 = Tuple('BUNDESLAND', [t, 'Bayern'])
    tuple3 = Tuple('STADT', [t, y])

    and2 = And(GreaterThan(y, 5), tuple3)
    fa1 = Forall(y, and2)
    or1 = Or(tuple2, fa1)
    ex2 = Exists(x, or1)
    and1 = And(tuple1, ex2)
    final = Exists(z, and1)

    result = Result([t])
    domain_calculus = DomainCalculus(result, final)
    print(domain_calculus)
    print('')
    print(domain_calculus.to_sql())

    print("\nPNF:\n")

    pnf = domain_calculus.to_normal_form()
    print(pnf)
    print('')
    print(domain_calculus.to_sql())
