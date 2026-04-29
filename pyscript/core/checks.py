from .constants import KEYWORDS, CONSTANT_KEYWORDS
from .mapping import BRACKETS_MAP
from .nodes import *
from .token import TOKENS

is_expression = frozenset([
    PysNumberNode, PysStringNode, PysKeywordNode, PysDebugNode, PysIdentifierNode, PysDictionaryNode, PysSetNode,
    PysListNode, PysTupleNode, PysAttributeNode, PysSubscriptNode, PysCallNode, PysChainOperatorNode,
    PysTernaryOperatorNode, PysBinaryOperatorNode, PysUnaryOperatorNode, PysIncrementalNode, PysMatchNode,
    PysFunctionNode, PysEllipsisNode
]).__contains__

is_statement = frozenset([
    PysStatementsNode, PysAssignmentNode, PysImportNode, PysIfNode, PysSwitchNode, PysTryNode, PysWithNode, PysForNode,
    PysWhileNode, PysDoWhileNode, PysRepeatNode, PysClassNode, PysGlobalNode, PysReturnNode, PysThrowNode,
    PysAssertNode, PysDeleteNode, PysContinueNode, PysBreakNode
]).__contains__

is_sequence = frozenset([
    PysSetNode, PysListNode, PysTupleNode
]).__contains__

is_constant = frozenset([
    PysKeywordNode, PysDebugNode
])

is_keyword = frozenset(KEYWORDS).__contains__
is_constant_keyword = frozenset(CONSTANT_KEYWORDS).__contains__

is_equal = frozenset([
    TOKENS['EQUAL'], TOKENS['EQUAL_COLON']
]).__contains__

is_blacklist_python_builtin = frozenset([
    'IndentationError', 'TabError', 'breakpoint', 'compile', 'copyright', 'credits', 'dir', 'eval', 'exec', 'help',
    'globals', 'license', 'locals', 'vars'
]).__contains__

is_python_extension = frozenset([
    '.cgi', '.fcgi', '.gyp', '.gypi', '.ipy', '.lmi', '.pxd', '.pxi', '.py', '.py3', '.pyc', '.pyd', '.pyde', '.pyi',
    '.pyo', '.pyp', '.pyproj', '.pyt', '.pyw', '.pyx', '.pyz', '.rpy', '.spec', '.tac', '.wsgi', '.xpy'
]).__contains__

is_left_bracket = frozenset(BRACKETS_MAP.keys()).__contains__
is_right_bracket = frozenset(BRACKETS_MAP.values()).__contains__
is_bracket = frozenset(BRACKETS_MAP.keys() | BRACKETS_MAP.values()).__contains__

is_private_attribute = lambda name : name.startswith('_') if isinstance(name, str) else name
is_public_attribute = lambda name : not name.startswith('_') if isinstance(name, str) else name