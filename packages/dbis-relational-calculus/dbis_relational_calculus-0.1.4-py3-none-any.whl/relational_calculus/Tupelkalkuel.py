from abc import ABC, abstractclassmethod
import py_compile


class TupleCalculus:
    def __init__(self, result, formula) -> None:
        assert isinstance(result, Result) and isinstance(formula, Formula)
        self.result = result
        self.formula = formula
        self.__verify()

    # verify the correctness of the result/formula combination (e.g. one must specify the type of a variable before returning it)
    def __verify(self) -> bool:
        # CONDITION: must return something
        if len(self.result.all_attributes + list(self.result.selected_attributes.keys())) <= 0:
            return False

        # CONDITION: no two variable can have the same name

        # CONDITION: every returned variable must have its type specified in every possible 'path'

        return True

    def __repr__(self) -> str:
        return f'\\{{{self.result} \\vert {self.formula}\\}}'

    def to_sql(self) -> str:
        # Get Types of return variables
        variables = self.result.all_attributes + \
            list(self.result.selected_attributes.keys())

        select_query = ''
        for variable in self.result.all_attributes:
            select_query += f'{variable.name}.*, '
        for variable, attribute in self.result.selected_attributes.items():
            select_query += f'{variable.name}.{attribute}, '
        select_query = select_query[:-len(', ')]

        from_query = ''
        for variable in variables:
            from_query += f'{variable.type} {variable.name}, '
        from_query = from_query[:-len(', ')]

        query = f'SELECT DISTINCT {select_query} FROM {from_query}'
        if self.formula.to_sql() != '':
            query += f' WHERE {self.formula.to_sql()}'
        return query


class Result:
    def __init__(self, all_attributes, selected_attributes) -> None:
        assert isinstance(all_attributes, list) and isinstance(
            selected_attributes, dict)
        # no variable (name) can be in all_attributes and selected_attributes
        assert len([key.name for key in selected_attributes.keys() if key.name in [
                   variable.name for variable in all_attributes]]) == 0
        self.all_attributes = all_attributes
        self.selected_attributes = selected_attributes

    def __repr__(self) -> str:
        output = '['
        for variable in self.all_attributes:
            output += f'\\text{{{variable.name}}}, '
        for variable, attribute in self.selected_attributes.items():
            output += f'\\text{{{variable.name}.{attribute}}}, '
        output = output[:-len(', ')]
        output += ']'
        return output


class Formula(ABC):
    def __init__(self, children) -> None:
        assert isinstance(children, list)
        self.children = children

    @abstractclassmethod
    def __repr__(self) -> str:
        pass

    @abstractclassmethod
    def to_sql(self) -> str:
        pass


class Variable(Formula):
    def __init__(self, name, type) -> None:
        assert isinstance(name, str) and isinstance(type, str)
        super().__init__([])
        self.name = name.lower()
        self.type = type.upper()

    def __repr__(self) -> str:
        return f'\\text{{{self.name}}} \\in \\text{{{self.type}}}'

    def to_sql(self) -> str:
        pass


class Equals(Formula):
    def __init__(self, left, right) -> None:
        assert not isinstance(
            left, Variable) and not isinstance(right, Variable)
        super().__init__([])
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        if isinstance(self.left, tuple):  # (variable, attr_name)
            left_string = f'\\text{{{self.left[0].name}.{self.left[1]}}}'
        else:
            left_string = f'\\text{{{self.left}}}'
        if isinstance(self.right, tuple):  # (variable, attr_name)
            right_string = f'\\text{{{self.right[0].name}.{self.right[1]}}}'
        else:
            right_string = f'\\text{{{self.right}}}'
        return f'{left_string} = {right_string}'

    def to_sql(self) -> str:
        if isinstance(self.left, tuple):  # (variable, attr_name)
            left_string = f'{self.left[0].name}.{self.left[1]}'
        elif isinstance(self.left, str):
            left_string = f'\'{self.left}\''
        else:
            left_string = f'{self.left}'
        if isinstance(self.right, tuple):  # (variable, attr_name)
            right_string = f'{self.right[0].name}.{self.right[1]}'
        elif isinstance(self.right, str):
            right_string = f'\'{self.right}\''
        else:
            right_string = f'{self.right}'
        return f'({left_string} = {right_string})'


class GreaterEquals(Formula):
    def __init__(self, left, right) -> None:
        assert not isinstance(
            left, Variable) and not isinstance(right, Variable)
        super().__init__([])
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        if isinstance(self.left, tuple):  # (variable, attr_name)
            left_string = f'\\text{{{self.left[0].name}.{self.left[1]}}}'
        else:
            left_string = f'\\text{{{self.left}}}'
        if isinstance(self.right, tuple):  # (variable, attr_name)
            right_string = f'\\text{{{self.right[0].name}.{self.right[1]}}}'
        else:
            right_string = f'\\text{{{self.right}}}'
        return f'{left_string} >= {right_string}'

    def to_sql(self) -> str:
        if isinstance(self.left, tuple):  # (variable, attr_name)
            left_string = f'{self.left[0].name}.{self.left[1]}'
        else:
            left_string = f'{self.left}'
        if isinstance(self.right, tuple):  # (variable, attr_name)
            right_string = f'{self.right[0].name}.{self.right[1]}'
        else:
            right_string = f'{self.right}'
        return f'({left_string} >= {right_string})'


class GreaterThan(Formula):
    def __init__(self, left, right) -> None:
        assert not isinstance(
            left, Variable) and not isinstance(right, Variable)
        super().__init__([])
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        if isinstance(self.left, tuple):  # (variable, attr_name)
            left_string = f'\\text{{{self.left[0].name}.{self.left[1]}}}'
        else:
            left_string = f'\\text{{{self.left}}}'
        if isinstance(self.right, tuple):  # (variable, attr_name)
            right_string = f'\\text{{{self.right[0].name}.{self.right[1]}}}'
        else:
            right_string = f'\\text{{{self.right}}}'
        return f'{left_string} > {right_string}'

    def to_sql(self) -> str:
        if isinstance(self.left, tuple):  # (variable, attr_name)
            left_string = f'{self.left[0].name}.{self.left[1]}'
        else:
            left_string = f'{self.left}'
        if isinstance(self.right, tuple):  # (variable, attr_name)
            right_string = f'{self.right[0].name}.{self.right[1]}'
        else:
            right_string = f'{self.right}'
        return f'({left_string} > {right_string})'


class LessEquals(Formula):
    def __init__(self, left, right) -> None:
        assert not isinstance(
            left, Variable) and not isinstance(right, Variable)
        super().__init__([])
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        if isinstance(self.left, tuple):  # (variable, attr_name)
            left_string = f'\\text{{{self.left[0].name}.{self.left[1]}}}'
        else:
            left_string = f'\\text{{{self.left}}}'
        if isinstance(self.right, tuple):  # (variable, attr_name)
            right_string = f'\\text{{{self.right[0].name}.{self.right[1]}}}'
        else:
            right_string = f'\\text{{{self.right}}}'
        return f'{left_string} \\leq {right_string}'

    def to_sql(self) -> str:
        if isinstance(self.left, tuple):  # (variable, attr_name)
            left_string = f'{self.left[0].name}.{self.left[1]}'
        else:
            left_string = f'{self.left}'
        if isinstance(self.right, tuple):  # (variable, attr_name)
            right_string = f'{self.right[0].name}.{self.right[1]}'
        else:
            right_string = f'{self.right}'
        return f'({left_string} <= {right_string})'


class LessThan(Formula):
    def __init__(self, left, right) -> None:
        assert not isinstance(
            left, Variable) and not isinstance(right, Variable)
        super().__init__([])
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        if isinstance(self.left, tuple):  # (variable, attr_name)
            left_string = f'\\text{{{self.left[0].name}.{self.left[1]}}}'
        else:
            left_string = f'\\text{{{self.left}}}'
        if isinstance(self.right, tuple):  # (variable, attr_name)
            right_string = f'\\text{{{self.right[0].name}.{self.right[1]}}}'
        else:
            right_string = f'\\text{{{self.right}}}'
        return f'{left_string} < {right_string}'

    def to_sql(self) -> str:
        if isinstance(self.left, tuple):  # (variable, attr_name)
            left_string = f'{self.left[0].name}.{self.left[1]}'
        else:
            left_string = f'{self.left}'
        if isinstance(self.right, tuple):  # (variable, attr_name)
            right_string = f'{self.right[0].name}.{self.right[1]}'
        else:
            right_string = f'{self.right}'
        return f'({left_string} < {right_string})'


class Exists(Formula):
    def __init__(self, variable, child) -> None:
        assert not isinstance(child, Variable)
        assert isinstance(variable, Variable)
        super().__init__([child])
        self.variable = variable

    def __repr__(self) -> str:
        return f'\\exists_{{{self.variable.name}}}(\\text{{{self.variable.name}}} \\in \\text{{{self.variable.type}}} \land ({self.children[0]}))'

    def to_sql(self) -> str:
        return f'EXISTS (SELECT * FROM {self.variable.type} AS {self.variable.name} WHERE ({self.children[0].to_sql()}))'


class Forall(Formula):
    def __init__(self, variable, child) -> None:
        assert not isinstance(child, Variable)
        assert isinstance(variable, Variable)
        super().__init__([child])
        self.variable = variable

    def __repr__(self) -> str:
        return f'\\forall_{{{self.variable.name}}}(\\text{{{self.variable.name}}} \\in \\text{{{self.variable.type}}} \land ({self.children[0]}))'

    def to_sql(self) -> str:
        return Not(Exists(self.variable, Not(self.children[0]))).to_sql()


class And(Formula):
    def __init__(self, child1, child2) -> None:
        super().__init__([child1, child2])

    def __repr__(self) -> str:
        return f'({self.children[0]}\\land {self.children[1]})'

    def to_sql(self) -> str:
        if isinstance(self.children[0], Variable) and isinstance(self.children[1], Variable):
            return f''
        if not isinstance(self.children[0], Variable) and isinstance(self.children[1], Variable):
            return f'{self.children[0].to_sql()}'
        if isinstance(self.children[0], Variable) and not isinstance(self.children[1], Variable):
            return f'{self.children[1].to_sql()}'
        return f'({self.children[0].to_sql()} AND {self.children[1].to_sql()})'


class Or(Formula):
    def __init__(self, child1, child2) -> None:
        super().__init__([child1, child2])

    def __repr__(self) -> str:
        return f'({self.children[0]} \\lor {self.children[1]})'

    def to_sql(self) -> str:
        if isinstance(self.children[0], Variable) and isinstance(self.children[1], Variable):
            return f''
        if not isinstance(self.children[0], Variable) and isinstance(self.children[1], Variable):
            return f'{self.children[0].to_sql()}'
        if isinstance(self.children[0], Variable) and not isinstance(self.children[1], Variable):
            return f'{self.children[1].to_sql()}'
        return f'({self.children[0].to_sql()} OR {self.children[1].to_sql()})'


class Not(Formula):
    def __init__(self, child) -> None:
        super().__init__([child])

    def __repr__(self) -> str:
        return f'\\neg({self.children[0]})'

    def to_sql(self) -> str:
        return f'(NOT {self.children[0].to_sql()})'


# temporary test to check the latex output
if __name__ == '__main__':
    t = Variable(name='t', type='KUNDE')
    a = Variable(name='a', type='KUNDE')
    p = Variable(name='p', type='PET')
    and_formula = And(GreaterEquals((t, 'age'), 5), LessThan((t, 'age'), 99))
    or_formula = Or(Or(Equals(5, 5), Exists(
        a, Not(Not(Equals((t, 'age'), 20))))), and_formula)
    result = Result(all_attributes=[p], selected_attributes={t: 'ort'})
    formula = And(Equals((p, 'id'), (t, 'pet_id')), And(p, And(t, or_formula)))
    tuple_calculus = TupleCalculus(result, formula)
    print(tuple_calculus)
    print('')
    print(tuple_calculus.to_sql())

    print('\n')

    tuple_calculus_2 = TupleCalculus(result, And(t, p))
    print(tuple_calculus_2)
    print('')
    print(tuple_calculus_2.to_sql())
