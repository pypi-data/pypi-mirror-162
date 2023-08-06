def add(d, label, obj, apply_to_tsapi=False):
    if apply_to_tsapi:
        if obj is not None:
            d[label] = obj.to_tsapi()
        return d
    else:
        if obj is not None:
            d[label] = obj
        return d


def parse(list_to_parse: list, obj: object) -> list:
    list_to_return = []
    if list_to_parse is not None:
        for list_item in list_to_parse:
            list_item_obj = obj(**list_item)
            list_to_return.append(list_item_obj)
    return list_to_return


def flatten_variable(variable, variable_list):
    if len(variable.looped_variables) > 0 and len(variable.values) > 0:
        for value in variable.values:
            _a = variable.to_dict()
            _a.update(value.to_dict())
            variable_list.append(_a)
        for loop_variable in variable.looped_variable_values:
            flatten_variable(variable=loop_variable,
                             variable_list=variable_list)
    elif len(variable.looped_variables) == 0 and len(variable.values) > 0:
        _a = variable.to_dict()
        for value in variable.values:
            _a = variable.to_dict()
            _a.update(value.to_dict())
            variable_list.append(_a)
    elif len(variable.looped_variables) > 0 and len(variable.values) == 0:
        # check if this is valid
        pass

    elif len(variable.looped_variables) == 0 and len(variable.values) == 0:
        _a = variable.to_dict()
        variable_list.append(_a)
    else:
        _a = variable.to_dict()
        variable_list.append(_a)
    if len(variable.otherSpecifyVariables) > 0:
        for osv in variable.otherSpecifyVariables:
            flatten_variable(variable=osv, variable_list=variable_list)

    return variable_list


class SurveyMetadata:
    def __init__(self, hierarchies=None, name="", title="", interviewCount=0,
                 languages=None, notAsked="", noAnswer="", variables=None,
                 sections=None):
        self.hierarchies = parse(hierarchies, Hierarchy)
        self.name = name
        self.title = title
        self.interview_count = interviewCount
        self.not_asked = notAsked
        self.no_answer = noAnswer
        self.variables = parse(variables, Variable)
        self.sections = parse(sections, Section)
        self.languages = parse(languages, Language)

    def __str__(self):
        return f'Name: {self.name}, Title {self.title}'

    def __repr__(self):
        return f'Survey({self.name})'

    def get_variables_list(self):
        variable_objects = ['variables',
                            'looped_variable',
                            'other_specify_variable',
                            ]
        objects_with_variables = ['survey', 'sections', 'hierarchies', ]
        objects_with_variables += variable_objects

        _dict = {}
        _dict = vars(self)

        return _dict

    def to_tsapi(self):
        _dict = {
            'hierarchies': [h.to_tsapi() for h in self.hierarchies],
            'name': self.name,
            'title': self.title,
            'interviewCount': self.interview_count,
            'languages': [lang.to_tsapi() for lang in self.languages],
            'notAsked': self.not_asked,
            'noAnswer': self.no_answer,
            'variables': [v.to_tsapi() for v in self.variables],
            'sections': [sect.to_tsapi() for sect in self.sections]
        }
        return _dict


class Section:
    def __init__(self, label, variables):
        self.label = Label(**label)
        self.sections = ""
        self.variables = parse(variables, Variable)

    def __str__(self):
        return f'{self.label}'

    def __repr__(self):
        return f'{self.label}'

    def to_tsapi(self):
        _dict = {
            'label': self.label.to_tsapi(),
            'variables': [v.to_tsapi() for v in self.variables]
        }
        return _dict


class Label:
    def __init__(self, text, altLabels=None):

        self.text = text
        self.alt_labels = parse(altLabels, AltLabel)

    def __str__(self):
        return self.text

    @property
    def label_analysis(self) -> str:
        alt_text = ""
        if self.alt_labels:
            for alts in self.alt_labels:
                if alts.mode == 'analysis':
                    alt_text = alts.text
                    return alt_text
        return alt_text

    @property
    def label_interview(self) -> str:
        alt_text = ""
        if self.alt_labels:
            for alts in self.alt_labels:
                if alts.mode == 'interview':
                    return alts.text
        return alt_text

    def to_tsapi(self):
        _dict = {}
        _dict = add(_dict, 'text', self.text)
        if len(self.alt_labels) > 0:
            _dict['altLabels'] = [al.to_tsapi() for al in self.alt_labels]
        return _dict


class Variable:
    def __init__(self,
                 ordinal=0,
                 label=None,
                 name="",
                 ident="",
                 type="",
                 values=None,
                 use="",
                 maxResponses=0,
                 loopedVariables=None,
                 otherSpecifyVariables=None):

        self.ident: str = ident
        self.ordinal: int = ordinal
        self.type: str = type
        self.name: str = name
        self.label: Label = Label(**label)
        self.use: str = use
        self.maxResponses: int = maxResponses
        self.otherSpecifyVariables = parse(otherSpecifyVariables,
                                           OtherSpecifyVariable)
        if values is None:
            values = {}
        self.variable_values = VariableValues(**values)

        self.looped_variables = parse(loopedVariables, LoopedVariable)

    def to_tsapi(self):

        _dict = {}
        _dict = add(_dict, 'ordinal', self.ordinal)
        _dict = add(_dict, 'label', self.label, True)
        _dict = add(_dict, 'name', self.name)
        _dict = add(_dict, 'ident', self.ident)
        _dict = add(_dict, 'type', self.type)
        _dict = add(_dict, 'values', self.variable_values, True)
        _dict = add(_dict, 'use', self.use)
        _dict = add(_dict, 'maxResponses', self.maxResponses)
        if len(self.looped_variables) > 0:
            _dict['loopedVariables'] = [lv.to_tsapi()
                                        for lv in self.looped_variables],
        if len(self.otherSpecifyVariables) > 0:
            _dict['otherSpecifyVariables'] = [o.to_tsapi() for o in
                                              self.otherSpecifyVariables],

        return _dict

    @property
    def looped_variable_values(self):
        looped_variable_value_list = []
        if len(self.values) == 0 | len(self.looped_variables) == 0:
            return looped_variable_value_list

        for value in self.values:
            for l_v in self.looped_variables:
                looped_variable_value_list.append(l_v)
        return looped_variable_value_list

    def __str__(self):
        return f'{self.ident}'

    def __repr__(self):
        return f'{self.ident}'

    @property
    def alt_labels(self):
        return self.label.alt_labels

    @property
    def label_text(self):
        return self.label.text

    @property
    def values(self):
        return self.variable_values.values

    @property
    def label_interview(self):
        return self.label.label_interview

    @property
    def label_analysis(self):
        return self.label.label_analysis

    @property
    def range_from(self):
        _r = ""
        if self.variable_values.range:
            _r = self.variable_values.range.range_from
        return _r

    @property
    def range_to(self):
        _r = ""
        if self.variable_values.range:
            _r = self.variable_values.range.range_to
        return _r

    def range(self):
        return self.variable_values.range

    def to_dict(self):
        _dict = {
            'var_name': self.name,
            'variable_name': self.name,
            'variable_ident': self.ident,
            'variable_label': self.label_text,
            'variable_type': self.type,
            'variable_interview_label': self.label_interview,
            'variable_analysis_label': self.label_analysis,
        }
        if self.range:
            _dict['variable_range_from'] = self.range_from
            _dict['variable_range_to'] = self.range_to
        return _dict


class Language:
    def __init__(self, ident="", name="", subLanguages=None):
        # if subLanguages is None:
        #     subLanguages = []
        self.ident = ident
        self.name = name
        self.sub_languages = parse(subLanguages, Language)

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f'language:{self.name}'

    def to_tsapi(self):
        _dict = {
            'ident': self.ident,
            'name': self.name
        }
        if len(self.sub_languages) > 0:
            _dict['subLanguage'] = [lang.to_tsapi()
                                    for lang in self.sub_languages]
        return _dict


class AltLabel:
    def __init__(self, mode='interview', text="", langIdent=""):
        self.mode = mode
        self.text = text
        self.langIdent = langIdent

    def __str__(self):
        return self.text

    def __repr__(self):
        return f'{self.mode} {self.text} {self.langIdent}'

    def to_tsapi(self):
        _dict = {
            'mode': self.mode,
            'text': self.text,
            'langIdent': self.langIdent
        }
        return _dict


class ValueRange:
    def __init__(self, **kwargs):
        self.range_from = kwargs['from']
        self.range_to = kwargs['to']

    def __repr__(self):
        return f'range: {self.range_from} - {self.range_to}'

    def to_tsapi(self):
        _dict = {
            'from': self.range_from,
            'to': self.range_to
        }
        return _dict


class ValueRef:
    def __init__(self, variableIdent="", valueIdent=""):
        self.variable_ident = variableIdent
        self.value_ident = valueIdent

    def __str__(self):
        a = f'variable_ident:{self.variable_ident}, ' \
            f'value_ident:{self.value_ident} '
        return a

    def __repr__(self):
        a = f'variable_ident:{self.variable_ident}, ' \
            f'value_ident:{self.value_ident} '
        return a

    def to_tsapi(self):
        _dict = {
            'variable_ident': self.variable_ident,
            'value_ident': self.value_ident
        }
        return _dict


class Value:
    def __init__(self, ident="", code="", label=None, score=0, ref=None):
        if ref is None:
            ref = {}
        if label is None:
            label = []

        self.ident = ident
        self.code = code
        self.label = Label(**label)
        self.score = score

        self.ref = None  # ValueRef(**ref)

    def to_tsapi(self):
        _dict = {}
        _dict = add(_dict, 'ident', self.ident)
        _dict = add(_dict, 'code', self.code)
        _dict = add(_dict, 'label', self.label, True)
        _dict = add(_dict, 'score', self.score)
        _dict = add(_dict, 'ref', self.ref)

        return _dict

    # @property
    # def label(self):
    #     return f'{self.ident} - {self._label.text}'

    def __str__(self):
        return f'{self.ident} - {self.label.text}'

    def __repr__(self):
        return self.label

    def to_dict(self):
        _dict = {
            'value_code': self.code,
            'value_ident': self.ident,
            'value_label': self.label.text,
            'value_score': self.score}
        return _dict


class VariableValues:
    def __init__(self, range=None, values=None):
        self.range = range

        self.values = parse(values, Value)

        if self.range is not None:
            self.range = ValueRange(**self.range)

    def to_tsapi(self):
        _dict = {}
        if self.values is not None:
            _dict['values'] = [val.to_tsapi() for val in self.values]
        if self.range is not None:
            _dict['range'] = self.range.to_tsapi()
        return _dict


class OtherSpecifyVariable(Variable):
    def __init__(self,
                 ordinal=0,
                 label=None,
                 name="",
                 ident="",
                 type="",
                 values=None,
                 use="",
                 maxResponses=0,
                 loopedVariables=None,
                 otherSpecifyVariables=None,
                 parentValueIdent=""):
        super().__init__(ordinal=ordinal,
                         label=label,
                         name=name,
                         ident=ident,
                         type=type,
                         values=values,
                         use=use,
                         maxResponses=maxResponses,
                         loopedVariables=loopedVariables,
                         otherSpecifyVariables=otherSpecifyVariables)
        self.parentValueIdent = parentValueIdent

    def to_tsapi(self):
        _dict = {}
        _dict = add(_dict, 'ordinal', self.ordinal)
        _dict = add(_dict, 'label', self.label, True)
        _dict = add(_dict, 'name', self.name)
        _dict = add(_dict, 'ident', self.ident)
        _dict = add(_dict, 'type', self.type)
        _dict = add(_dict, 'values', self.variable_values, True)
        _dict = add(_dict, 'use', self.use)
        _dict = add(_dict, 'maxResponses', self.maxResponses)
        _dict['loopedVariables'] = [lv.to_tsapi() for lv in
                                    self.looped_variables]
        _dict['otherSpecifyVariables'] = [o.to_tsapi() for o in
                                          self.otherSpecifyVariables]

        _dict = add(_dict, 'parentValueIdent', self.parentValueIdent)

        return _dict


class LoopedVariable(Variable):

    def __init__(self,
                 ordinal=0,
                 label=None,
                 name="",
                 ident="",
                 type="",
                 values=None,
                 use="",
                 maxResponses=0,
                 loopedVariables=None,
                 otherSpecifyVariables=None,
                 loop_ref=None):
        super().__init__(ordinal=ordinal,
                         label=label,
                         name=name,
                         ident=ident,
                         type=type,
                         values=values,
                         use=use,
                         maxResponses=maxResponses,
                         loopedVariables=loopedVariables,
                         otherSpecifyVariables=otherSpecifyVariables)

        self.loop_ref = loop_ref

    def to_tsapi(self):
        _dict = {}
        _dict = add(_dict, 'ordinal', self.ordinal)
        _dict = add(_dict, 'label', self.label, True)
        _dict = add(_dict, 'name', self.name)
        _dict = add(_dict, 'ident', self.ident)
        _dict = add(_dict, 'type', self.type)
        _dict = add(_dict, 'values', self.variable_values, True)
        _dict = add(_dict, 'use', self.use)
        _dict = add(_dict, 'maxResponses', self.maxResponses)
        _dict['loopedVariables'] = [lv.to_tsapi() for lv in
                                    self.looped_variables]
        _dict['otherSpecifyVariables'] = [o.to_tsapi() for o in
                                          self.otherSpecifyVariables]
        _dict = add(_dict, 'loopRef', self.loop_ref, True)

        return _dict

    @property
    def parent_variable_ident(self):
        if self.loop_ref is not None:
            return self.loop_ref.variable_ident
        else:
            return ""

    @property
    def parent_value_ident(self):
        if self.loop_ref is not None:
            return self.loop_ref.value_ident
        else:
            return ""

    def to_dict(self):
        _dict = {
            'var_name': self.name,
            'variable_name': self.name,
            'variable_ident': self.ident,
            'variable_label': self.label_text,
            'variable_type': self.type,
            'variable_interview_label': self.label_interview,
            'variable_analysis_label': self.label_analysis,
            'parent_variable_label': self.parent_variable_ident,
            'parent_value_label': self.parent_value_ident,

        }
        if self.range:
            _dict['variable_range_from'] = self.range_from
            _dict['variable_range_to'] = self.range_to
        return _dict

    def __str__(self):
        return f'{self.name} - {self.parent_value_ident}'

    def __repr__(self):
        return f'{self.name}'


class Hierarchy:
    def __init__(self, ident: str = "", parent=None, metadata=None):
        if metadata is None:
            metadata = {}
        if parent is None:
            parent = {}
        self.ident: str = ident
        self.parent: ParentDetails = parent
        self.metadata: MetaData = metadata

    def to_tsapi(self):
        _dict = {
            'ident': self.ident,
            'metadata': self.metadata.to_tsapi(),
            'parent': self.parent
        }


class ParentDetails:
    def __init__(self, level, linkVar, ordered):
        self.level = level
        self.link_var = linkVar
        self.ordered = ordered


class MetaData:
    def __init__(self, name="", title="", interviewCount=0, languages=None,
                 notAsked="", noAnswer="", variables=None, sections=None):
        self.name = name
        self.title = title
        self.interview_count = interviewCount
        self.not_asked = notAsked
        self.no_answer = noAnswer
        self.sections = parse(sections, Section)
        self.variables = parse(variables, Variable)
        self.languages = parse(languages, Language)

    def to_tsapi(self):
        _dict = {
            'name': self.name,
            'title': self.name,
            'interviewCount': self.interview_count,
            'notAsked': self.not_asked,
            'noAnswer': self.no_answer,
            'variables': [var.to_tsapi() for var in self.variables],
            'sections': [sect.to_tsapi() for sect in self.sections],
            'languages': [lang.to_tsapi() for lang in self.languages],
        }
        return _dict


class InterviewsQuery:
    def __init__(self,
                 surveyId="",
                 start=0,
                 maxLength=0,
                 completeOnly=True,
                 variables=None,
                 interviewIdents=None,
                 date=""):
        self.survey_id = surveyId
        self.start = start
        self.max_length = maxLength
        self.complete_only = completeOnly
        self.variables = variables
        self.interview_idents = interviewIdents
        self.date = date


class LoopedDataItem:
    def __init__(self,
                 parent="",
                 ident="",
                 values=None,
                 loopedDataItems=None,
                 ):
        self.parent = parent
        self.ident = ident
        self.values = [v for v in values]

        if loopedDataItems is not None:
            self.looped_data_items = [LoopedDataItem(**lr)
                                      for lr in loopedDataItems]
        else:
            self.looped_data_items = None

    def to_tsapi(self):
        _dict = {'parent': self.parent,
                 'ident': self.ident,
                 'values': self.values}
        if self.looped_data_items:
            _dict['loopedDataItems'] = [ldi.to_tsapi() for ldi in
                                        self.looped_data_items]
        return _dict


class DataItem:
    def __init__(self, ident="", values=None, loopedDataItems=None):
        self.ident = ident
        self.values = [v for v in values]
        self.looped_data_items = []
        if loopedDataItems is not None:
            self.looped_data_items = [LoopedDataItem(**lr)
                                      for lr in loopedDataItems]
        else:
            self.looped_data_items = None

    def to_tsapi(self):
        _dict = {'ident': self.ident,
                 'values': self.values}

        if self.looped_data_items:
            _dict['loopedDataItems'] = [ldi.to_tsapi()
                                        for ldi in self.looped_data_items]

        return _dict


class Level:
    def __init__(self, ident=""):
        self.ident = ident

    def to_tsapi(self):
        _dict = {'ident': self.ident}
        return _dict


class HierarchicalInterview:
    def __init__(self, level=None, ident="", date="", complete=True,
                 dataItems=None, hierarchicalInterviews=None):
        self.level = Level(**level)
        self.ident = ident
        self.date = date
        self.complete = complete
        self.data_items = parse(dataItems, DataItem)
        self.hierarchical_interviews = parse(hierarchicalInterviews,
                                             HierarchicalInterview)

    def to_tsapi(self):
        _dict = {'level': self.level.to_tsapi(),
                 'ident': self.ident,
                 'date': self.date,
                 'complete': self.complete,
                 'dataItems': [di.to_tsapi() for di in self.data_items],
                 'hierarchicalInterviews': [hi.to_tsapi() for hi in
                                            self.hierarchical_interviews]}
        return _dict


class Interview:
    def __init__(self, ident="", date="", complete=True, dataItems=None,
                 hierarchicalInterviews=None):
        self.ident = ident
        self.date = date
        self.complete = complete
        self.data_items = parse(dataItems, DataItem)
        self.hierarchical_interviews = parse(hierarchicalInterviews,
                                             HierarchicalInterview)

    def to_tsapi(self):
        _dict = {'ident': self.ident,
                 'date': self.date,
                 'complete': self.complete,
                 'dataItems': [di.to_tsapi() for di in self.data_items]}
        if self.hierarchical_interviews:
            _dict['hierarchicalInterviews'] = [hi.to_tsapi() for hi in
                                               self.hierarchical_interviews]

        return _dict
