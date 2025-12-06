from .constants import TOKENS, KEYWORDS
from .mapping import PARENTHESISES_MAP
from .nodes import *

is_expression = frozenset([
    PysNumberNode, PysStringNode, PysKeywordNode, PysIdentifierNode, PysDictionaryNode, PysSetNode, PysListNode,
    PysTupleNode, PysAttributeNode, PysSubscriptNode, PysCallNode, PysChainOperatorNode, PysTernaryOperatorNode,
    PysBinaryOperatorNode, PysUnaryOperatorNode, PysFunctionNode, PysEllipsisNode
]).__contains__

is_statement = frozenset([
    PysStatementsNode, PysAssignNode, PysImportNode, PysIfNode, PysSwitchNode, PysTryNode, PysWithNode, PysForNode,
    PysWhileNode, PysDoWhileNode, PysClassNode, PysGlobalNode, PysReturnNode, PysThrowNode, PysAssertNode,
    PysDeleteNode, PysContinueNode, PysBreakNode
]).__contains__

is_assign = frozenset([
    PysSetNode, PysListNode, PysTupleNode
]).__contains__

is_keyword = frozenset(KEYWORDS.values()).__contains__

is_python_extensions = frozenset([
    '.py', '.ipy', '.pyc', '.pyd', '.pyi', '.pyo', '.pyp', '.pyw', '.pyz', '.rpy', '.xpy', '.pyproj'
]).__contains__

is_equals = frozenset([
    TOKENS['EQUAL'], TOKENS['EQUAL-COLON']
]).__contains__

is_incremental = frozenset([
    TOKENS['DOUBLE-PLUS'], TOKENS['DOUBLE-MINUS']
]).__contains__

is_blacklist_python_builtins = frozenset([
    'IndentationError', 'TabError', 'compile', 'copyright', 'credits', 'dir', 'eval', 'exec', 'help', 'globals',
    'license', 'locals', 'vars'
]).__contains__

is_left_parenthesis = frozenset(PARENTHESISES_MAP.keys()).__contains__
is_right_parenthesis = frozenset(PARENTHESISES_MAP.values()).__contains__
is_parenthesis = frozenset(PARENTHESISES_MAP.keys() | PARENTHESISES_MAP.values()).__contains__

is_constant_keywords = frozenset([
    KEYWORDS['__debug__'], KEYWORDS['of'], KEYWORDS['in'], KEYWORDS['is'], KEYWORDS['and'], KEYWORDS['or'],
    KEYWORDS['not'], KEYWORDS['False'], KEYWORDS['None'], KEYWORDS['True'], KEYWORDS['class'], KEYWORDS['false'],
    KEYWORDS['func'], KEYWORDS['function'], KEYWORDS['global'], KEYWORDS['none'], KEYWORDS['true']
]).__contains__

is_private_attribute = lambda name : name.startswith('_')
is_public_attribute = lambda name : not name.startswith('_')