import traceback

from .dirutils import joiner
from .fileutils import append_file, file_write
from .utils import env_get

TAB_SPACE_MULT = 2
TAB = " " * TAB_SPACE_MULT
JSON_INDENT = TAB_SPACE_MULT
TABS = TAB * 2
SCHNELL_BASEDIR = env_get("ULIBPY_BASEDIR")
if SCHNELL_BASEDIR:
    TEMPLATESDIR = joiner(SCHNELL_BASEDIR, "db/bantuan/templates")


type_mapper_by_provider = {
    "django_orm": {
        "array_of": "ARRAY(__SUBTYPE__)",
        "empty_array": "Array",
        "auto": "{ type: Number, required: true, }",
        "bigint": "BIGINT",
        "blob": "String",
        "boolean": "BOOLEAN",
        "date": "DATE",
        "decimal": "DECIMAL",
        "django_many_to_many": "[{ type: String }]",
        "django_one_to_many": "String",
        "django_one_to_one": "[{ type: String }]",
        "django_foreign_key": "{ type: STRING, allowNull: false, references: __DQModelRujukan__DQ, }",
        "double": "DOUBLE",
        "enum": "ENUM",
        "float": "FLOAT",
        "image": "STRING",
        "integer": "INTEGER",
        "number": "DECIMAL",
        "serial": "String",
        "slug": "STRING",
        "string": "STRING",
        "text": "TEXT",
        "timestamp": '"TIMESTAMP"',
        "uuid": "UUID",
        "uuidv1": "UUIDV1",
        "uuidv4": "UUIDV4",
        "varchar": "STRING",
    },
    "hibernate": {
        "array_of": "ARRAY(__SUBTYPE__)",
        "empty_array": "Array",
        "auto": "{ type: Number, required: true, }",
        "bigint": "BIGINT",
        "blob": "String",
        "boolean": "BOOLEAN",
        "date": "DATE",
        "decimal": "DECIMAL",
        "django_many_to_many": "[{ type: String }]",
        "django_one_to_many": "String",
        "django_one_to_one": "[{ type: String }]",
        "django_foreign_key": "{ type: STRING, allowNull: false, references: __DQModelRujukan__DQ, }",
        "double": "DOUBLE",
        "enum": "ENUM",
        "float": "FLOAT",
        "image": "STRING",
        "integer": "INTEGER",
        "number": "DECIMAL",
        "serial": "String",
        "slug": "STRING",
        "string": "STRING",
        "text": "TEXT",
        "timestamp": '"TIMESTAMP"',
        "uuid": "UUID",
        "uuidv1": "UUIDV1",
        "uuidv4": "UUIDV4",
        "varchar": "STRING",
    },
    "mongoose": {
        "array_of": "Array",
        "empty_array": "Array",
        "auto": "String",
        "bigint": "String",
        "blob": "String",
        "boolean": "Boolean",
        "date": "Date",
        "decimal": "Schema.Types.Decimal128",
        "django_many_to_many": "Schema.Types.ObjectId",
        "django_one_to_many": "Schema.Types.ObjectId",
        "django_one_to_one": "Schema.Types.ObjectId",
        "django_foreign_key": "Schema.Types.ObjectId",
        "double": "Number",
        "enum": "String",
        "float": "Number",
        "image": "String",
        "integer": "Number",
        "number": "String",
        "serial": "String",
        "slug": "String",
        "string": "String",
        "text": "String",
        "timestamp": "Date",
        "uuid": "Schema.Types.ObjectId",
        "uuidv1": "Schema.Types.ObjectId",
        "uuidv4": "Schema.Types.ObjectId",
        "varchar": "String",
    },
    "mybatis": {
        "array_of": "ARRAY(__SUBTYPE__)",
        "empty_array": "Array",
        "auto": "{ type: Number, required: true, }",
        "bigint": "BIGINT",
        "blob": "String",
        "boolean": "BOOLEAN",
        "date": "DATE",
        "decimal": "DECIMAL",
        "django_many_to_many": "[{ type: String }]",
        "django_one_to_many": "String",
        "django_one_to_one": "[{ type: String }]",
        "django_foreign_key": "{ type: STRING, allowNull: false, references: __DQModelRujukan__DQ, }",
        "double": "DOUBLE",
        "enum": "ENUM",
        "float": "FLOAT",
        "image": "STRING",
        "integer": "INTEGER",
        "number": "DECIMAL",
        "serial": "String",
        "slug": "STRING",
        "string": "STRING",
        "text": "TEXT",
        "timestamp": '"TIMESTAMP"',
        "uuid": "UUID",
        "uuidv1": "UUIDV1",
        "uuidv4": "UUIDV4",
        "varchar": "STRING",
    },
    "nest_mongo": {
        "array_of": "ARRAY(__SUBTYPE__)",
        "empty_array": "Array",
        "auto": "{ type: Number, required: true, }",
        "bigint": "BIGINT",
        "blob": "String",
        "boolean": "BOOLEAN",
        "date": "DATE",
        "decimal": "DECIMAL",
        "django_many_to_many": "[{ type: String }]",
        "django_one_to_many": "String",
        "django_one_to_one": "[{ type: String }]",
        "django_foreign_key": "{ type: STRING, allowNull: false, references: __DQModelRujukan__DQ, }",
        "double": "DOUBLE",
        "enum": "ENUM",
        "float": "FLOAT",
        "image": "STRING",
        "integer": "INTEGER",
        "number": "DECIMAL",
        "serial": "String",
        "slug": "STRING",
        "string": "STRING",
        "text": "TEXT",
        "timestamp": '"TIMESTAMP"',
        "uuid": "UUID",
        "uuidv1": "UUIDV1",
        "uuidv4": "UUIDV4",
        "varchar": "STRING",
    },
    "nest_postgres": {
        "array_of": "ARRAY(__SUBTYPE__)",
        "empty_array": "Array",
        "auto": "{ type: Number, required: true, }",
        "bigint": "BIGINT",
        "blob": "String",
        "boolean": "BOOLEAN",
        "date": "DATE",
        "decimal": "DECIMAL",
        "django_many_to_many": "[{ type: String }]",
        "django_one_to_many": "String",
        "django_one_to_one": "[{ type: String }]",
        "django_foreign_key": "{ type: STRING, allowNull: false, references: __DQModelRujukan__DQ, }",
        "double": "DOUBLE",
        "enum": "ENUM",
        "float": "FLOAT",
        "image": "STRING",
        "integer": "INTEGER",
        "number": "DECIMAL",
        "serial": "String",
        "slug": "STRING",
        "string": "STRING",
        "text": "TEXT",
        "timestamp": '"TIMESTAMP"',
        "uuid": "UUID",
        "uuidv1": "UUIDV1",
        "uuidv4": "UUIDV4",
        "varchar": "STRING",
    },
    "prisma": {
        "array_of": "[]",
        "empty_array": "Array",
        "auto": "String",
        "bigint": "String",
        "blob": "String",
        "boolean": "Boolean",
        "date": "Date",
        "decimal": "String",
        "django_many_to_many": "String",
        "django_one_to_many": "String",
        "django_one_to_one": "String",
        "django_foreign_key": "String",
        "double": "Number",
        "enum": "String",
        "float": "Number",
        "image": "String",
        "integer": "Int",
        "number": "String",
        "serial": "String",
        "slug": "String",
        "string": "String",
        "text": "String",
        "timestamp": "DateTime",
        "uuid": "String",
        "uuidv1": "String",
        "uuidv4": "String",
        "varchar": "String",
    },
    "sequelize": {
        "array_of": "ARRAY(__SUBTYPE__)",
        "empty_array": "Array",
        "auto": "{ type: Number, required: true, }",
        "bigint": "BIGINT",
        "blob": "String",
        "boolean": "BOOLEAN",
        "date": "DATE",
        "decimal": "DECIMAL",
        "django_many_to_many": "[{ type: String }]",
        "django_one_to_many": "String",
        "django_one_to_one": "[{ type: String }]",
        "django_foreign_key": '{ type: STRING, allowNull: false, references: "ModelRujukan", }',
        "double": "DOUBLE",
        "enum": "ENUM",
        "float": "FLOAT",
        "image": "STRING",
        "integer": "INTEGER",
        "number": "DECIMAL",
        "serial": "String",
        "slug": "STRING",
        "string": "STRING",
        "text": "TEXT",
        "timestamp": '"TIMESTAMP"',
        "uuid": "UUID",
        "uuidv1": "UUIDV1",
        "uuidv4": "UUIDV4",
        "varchar": "STRING",
    },
    "sql_mssql": {
        "array_of": "ARRAY(__SUBTYPE__)",
        "empty_array": "Array",
        "auto": "{ type: Number, required: true, }",
        "bigint": "BIGINT",
        "blob": "String",
        "boolean": "BOOLEAN",
        "date": "DATE",
        "decimal": "DECIMAL",
        "django_many_to_many": "[{ type: String }]",
        "django_one_to_many": "String",
        "django_one_to_one": "[{ type: String }]",
        "django_foreign_key": "{ type: STRING, allowNull: false, references: __DQModelRujukan__DQ, }",
        "double": "DOUBLE",
        "enum": "ENUM",
        "float": "FLOAT",
        "image": "STRING",
        "integer": "INTEGER",
        "number": "DECIMAL",
        "serial": "String",
        "slug": "STRING",
        "string": "STRING",
        "text": "TEXT",
        "timestamp": '"TIMESTAMP"',
        "uuid": "UUID",
        "uuidv1": "UUIDV1",
        "uuidv4": "UUIDV4",
        "varchar": "STRING",
    },
    "sql_mysql": {
        "array_of": "Array",
        "empty_array": "Array",
        "auto": "String",
        "bigint": "String",
        "blob": "String",
        "boolean": "BOOLEAN",
        "date": "Date",
        "decimal": "Schema.Types.Decimal128",
        "django_many_to_many": "Schema.Types.ObjectId",
        "django_one_to_many": "Schema.Types.ObjectId",
        "django_one_to_one": "Schema.Types.ObjectId",
        "django_foreign_key": "Schema.Types.ObjectId",
        "double": "Number",
        "enum": "String",
        "float": "Number",
        "image": "String",
        "integer": "INT",  # id INT PRIMARY KEY
        "number": "String",
        "serial": "String",
        "slug": "String",
        "string": "String",
        "text": "String",
        "timestamp": "Date",
        "uuid": "Schema.Types.ObjectId",
        "uuidv1": "Schema.Types.ObjectId",
        "uuidv4": "Schema.Types.ObjectId",
        "varchar": "String",
    },
    "sql_postgres": {
        "array_of": "ARRAY(__SUBTYPE__)",
        "empty_array": "Array",
        "auto": "{ type: Number, required: true, }",
        "bigint": "BIGINT",
        "blob": "String",
        "boolean": "BOOLEAN",
        "date": "DATE",
        "decimal": "DECIMAL",
        "django_many_to_many": "[{ type: String }]",
        "django_one_to_many": "String",
        "django_one_to_one": "[{ type: String }]",
        "django_foreign_key": "{ type: STRING, allowNull: false, references: __DQModelRujukan__DQ, }",
        "double": "DOUBLE",
        "enum": "ENUM",
        "float": "FLOAT",
        "image": "STRING",
        "integer": "INTEGER",
        "number": "DECIMAL",
        "serial": "String",
        "slug": "STRING",
        "string": "STRING",
        "text": "TEXT",
        "timestamp": '"TIMESTAMP"',
        "uuid": "UUID",
        "uuidv1": "UUIDV1",
        "uuidv4": "UUIDV4",
        "varchar": "STRING",
    },
    "sql_sqlite": {
        "array_of": "ARRAY(__SUBTYPE__)",
        "empty_array": "Array",
        "auto": "{ type: Number, required: true, }",
        "bigint": "BIGINT",
        "blob": "String",
        "boolean": "BOOLEAN",
        "date": "DATE",
        "decimal": "DECIMAL",
        "django_many_to_many": "[{ type: String }]",
        "django_one_to_many": "String",
        "django_one_to_one": "[{ type: String }]",
        "django_foreign_key": "{ type: STRING, allowNull: false, references: __DQModelRujukan__DQ, }",
        "double": "DOUBLE",
        "enum": "ENUM",
        "float": "FLOAT",
        "image": "STRING",
        "integer": "INTEGER",
        "number": "DECIMAL",
        "serial": "String",
        "slug": "STRING",
        "string": "STRING",
        "text": "TEXT",
        "timestamp": '"TIMESTAMP"',
        "uuid": "UUID",
        "uuidv1": "UUIDV1",
        "uuidv4": "UUIDV4",
        "varchar": "STRING",
    },
    "struct_go": {
        # 'array_of'            : 'ARRAY(__SUBTYPE__)',
        "array_of": "__SUBTYPE__[]",
        "empty_array": "[]",
        "auto": "{ type: Number, required: true, }",
        "bigint": "BIGINT",
        "blob": "String",
        "boolean": "BOOLEAN",
        "date": "DATE",
        "decimal": "DECIMAL",
        "django_many_to_many": "[{ type: String }]",
        "django_one_to_many": "String",
        "django_one_to_one": "[{ type: String }]",
        "django_foreign_key": "{ type: STRING, allowNull: false, references: __DQModelRujukan__DQ, }",
        "double": "DOUBLE",
        "enum": "ENUM",
        "float": "FLOAT",
        "image": "STRING",
        "integer": "INTEGER",
        "number": "DECIMAL",
        "serial": "String",
        "slug": "STRING",
        "string": "STRING",
        "text": "TEXT",
        "timestamp": '"TIMESTAMP"',
        "uuid": "UUID",
        "uuidv1": "UUIDV1",
        "uuidv4": "UUIDV4",
        "varchar": "STRING",
    },
    "struct_kt": {
        # 'array_of'            : 'ARRAY(__SUBTYPE__)',
        "array_of": "__SUBTYPE__[]",
        "empty_array": "[]",
        "auto": "{ type: Number, required: true, }",
        "bigint": "BIGINT",
        "blob": "String",
        "boolean": "BOOLEAN",
        "date": "DATE",
        "decimal": "DECIMAL",
        "django_many_to_many": "[{ type: String }]",
        "django_one_to_many": "String",
        "django_one_to_one": "[{ type: String }]",
        "django_foreign_key": "{ type: STRING, allowNull: false, references: __DQModelRujukan__DQ, }",
        "double": "DOUBLE",
        "enum": "ENUM",
        "float": "FLOAT",
        "image": "STRING",
        "integer": "INTEGER",
        "number": "DECIMAL",
        "serial": "String",
        "slug": "STRING",
        "string": "STRING",
        "text": "TEXT",
        "timestamp": '"TIMESTAMP"',
        "uuid": "UUID",
        "uuidv1": "UUIDV1",
        "uuidv4": "UUIDV4",
        "varchar": "STRING",
    },
    "struct_rs": {
        # 'array_of'            : 'ARRAY(__SUBTYPE__)',
        "array_of": "__SUBTYPE__[]",
        "empty_array": "[]",
        "auto": "{ type: Number, required: true, }",
        "bigint": "BIGINT",
        "blob": "String",
        "boolean": "BOOLEAN",
        "date": "DATE",
        "decimal": "DECIMAL",
        "django_many_to_many": "[{ type: String }]",
        "django_one_to_many": "String",
        "django_one_to_one": "[{ type: String }]",
        "django_foreign_key": "{ type: STRING, allowNull: false, references: __DQModelRujukan__DQ, }",
        "double": "DOUBLE",
        "enum": "ENUM",
        "float": "FLOAT",
        "image": "STRING",
        "integer": "INTEGER",
        "number": "DECIMAL",
        "serial": "String",
        "slug": "STRING",
        "string": "STRING",
        "text": "TEXT",
        "timestamp": '"TIMESTAMP"',
        "uuid": "UUID",
        "uuidv1": "UUIDV1",
        "uuidv4": "UUIDV4",
        "varchar": "STRING",
    },
    "struct_ts": {
        # 'array_of'            : 'ARRAY(__SUBTYPE__)',
        "array_of": "__SUBTYPE__[]",
        "empty_array": "[]",
        "auto": "{ type: number, required: true, }",
        "bigint": "number",
        "blob": "string",
        "boolean": "boolean",
        "date": "string",
        "decimal": "number",
        "django_many_to_many": "[{ type: string }]",
        "django_one_to_many": "string",
        "django_one_to_one": "[{ type: string }]",
        "django_foreign_key": "{ type: string, allowNull: false, references: __DQModelRujukan__DQ, }",
        "double": "number",
        "enum": "string",
        "float": "number",
        "image": "string",
        "integer": "number",
        "number": "number",
        "serial": "string",
        "slug": "string",
        "string": "string",
        "text": "string",
        "timestamp": "string",
        "uuid": "string",
        "uuidv1": "string",
        "uuidv4": "string",
        "varchar": "string",
    },
}

type_mapper = {
    "empty_array": {
        "mongoose": "[]",
        "sequelize": "ARRAY",
    },
    "array_of": {
        "mongoose": "Array",
        "sequelize": "ARRAY(__SUBTYPE__)",
    },
    "auto": {
        "django": "models.AutoField",
        "flask": "sqlalchemy.Integer",
        "graphene": "graphene.ID",
        "pydantic": "int",
        "sequelize": "{ type: Number, required: true, }",
        "sqlalchemy": "Integer",
    },
    "bigint": {
        "django": "BIGINT",
        "flask": "sqlalchemy.Integer",
        "graphene": "graphene.Int",
        "pydantic": "int",
        "sequelize": "BIGINT",
        "sqlalchemy": "Integer",
    },
    "blob": {},
    "boolean": {
        "django": "models.BooleanField",
        "flask": "sqlalchemy.Boolean",
        "graphene": "graphene.Boolean",
        "mongoose": "Boolean",
        "pydantic": "bool",
        "sboot": "Boolean",
        "sequelize": "BOOLEAN",
        "sqlalchemy": "Boolean",
    },
    "date": {
        "django": "models.DateField",
        "flask": "sqlalchemy.DateTime",
        "graphene": "graphene.types.datetime.DateTime",
        "mongoose": "Date",
        "pydantic": "datetime.date",
        "sequelize": "DATE",
        "sqlalchemy": "DateTime",
    },
    "decimal": {
        "django": "models.DecimalField",
        "sequelize": "DECIMAL",
    },
    "double": {
        "django": "DOUBLE",
        "sequelize": "DOUBLE",
    },
    "email": {
        "django": "models.EmailField",
    },
    "enum": {
        "django": "ENUM",
        "sequelize": "ENUM",
    },
    "float": {
        "django": "FLOAT",
        "flask": "sqlalchemy.Float",
        "graphene": "graphene.Float",
        "nest": "number",
        "pydantic": "float",
        "sboot": "Float",
        "sequelize": "FLOAT",
        "sqlalchemy": "Float",
    },
    "id": {
        "graphene": "graphene.ID",
    },
    "image": {
        "django": "models.ImageField",
        "sequelize": "STRING",
    },
    "integer": {
        "django": "models.IntegerField",
        "flask": "sqlalchemy.Integer",
        "graphene": "graphene.Int",
        "pydantic": "int",
        "sboot": "Int",
        "sequelize": "INTEGER",
        "sqlalchemy": "Integer",
    },
    "number": {
        "django": "NUMBER",
        "mongoose": "Number",
        "sequelize": "DECIMAL",
    },
    "serial": {
        "flask": "sqlalchemy.Integer",
    },
    "slug": {
        "django": "models.SlugField",
        "sequelize": "STRING",
    },
    "string": {
        "django": "models.CharField",
        "djongo": "models.CharField",
        "flask": "sqlalchemy.String",
        "graphene": "graphene.String",
        "mongoose": "String",
        "nest": "string",
        "pydantic": "str",
        "sboot": "String",
        "sequelize": "STRING",
        "sqlalchemy": "String",
    },
    "text": {
        "django": "models.TextField",
        "djongo": "models.CharField",
        "flask": "sqlalchemy.Text",
        "graphene": "graphene.String",
        "pydantic": "str",
        "sequelize": "TEXT",
        "sqlalchemy": "Text",
    },
    "timestamp": {
        # apa beda auto_now=True dan auto_now_add=True?
        "django": "models.DateTimeField",
        "djongo": "models.DateTimeField",
        "flask": "sqlalchemy.TimeStamp",
        "graphene": "graphene.types.datetime.DateTime",
        "pydantic": "datetime.datetime",
        "sequelize": "TEXT",
        "sequelize": "__DQTIMESTAMP__DQ",
        "sqlalchemy": "TimeStamp",
    },
    "url": {
        "djongo": "models.URLField",
    },
    "uuid": {
        "sequelize": "UUID",
    },
    "uuid1": {
        "sequelize": "UUIDV1",
    },
    "uuid4": {
        "sequelize": "UUIDV4",
    },
    "varchar": {
        "django": "models.CharField",
        "flask": "sqlalchemy.String",
        "graphene": "graphene.String",
        "pydantic": "str",
        "sequelize": "STRING",
        "sqlalchemy": "String",
    },
    # django specific
    "django_foreign_key": {
        "django": "models.ForeignKey",
        "djongo": "models.ForeignKey",
        "flask": "sqlalchemy.ForeignKey",
        "mongoose": "Schema.ObjectId",
        "sequelize": "{ type: STRING, allowNull: false, references: __DQModelRujukan__DQ, }",
    },
    "django_one_to_one": {
        "django": "models.OneToOneField",
        "sequelize": "[{ type: String }]",
    },
    "django_one_to_many": {
        "django": "models.OneToManyField",
    },
    "django_many_to_many": {
        "django": "models.ManyToManyField",
        "sequelize": "[{ type: String }]",
    },
}


def columnify(tables, provider="django"):
    tables_with_columns = {}
    table_attributes = {}
    for tblidx, tbl in enumerate(tables, 1):
        tablename_lower = tbl.model.lower()
        tablename_case = tbl.model
        columns_with_types = []
        columns_names = []
        for colidx, column in enumerate(tbl.children):
            mapper = type_mapper.get(provider, "default")
            tipe_kolom = mapper.get(column.type, column.type)
            nama_kolom = column.label
            coltype = f"{nama_kolom}: {tipe_kolom}"
            colname = nama_kolom

            if hasattr(column, "allowNull"):
                pass
            if hasattr(column, "auto_increment"):
                pass
            if hasattr(column, "auto_now"):
                pass
            if hasattr(column, "auto_now_add"):
                pass
            if hasattr(column, "blank"):
                pass
            if hasattr(column, "db_index"):
                pass
            if hasattr(column, "decimal_places"):
                pass
            if hasattr(column, "default"):
                pass
            if hasattr(column, "defaultValue"):
                pass
            if hasattr(column, "editable"):
                pass
            if hasattr(column, "foreignKeyOnDelete"):
                pass
            if hasattr(column, "max_length"):
                pass
            if hasattr(column, "max_digits"):
                pass
            if hasattr(column, "primaryKey"):
                pass
            if hasattr(column, "references"):
                pass
            if hasattr(column, "referencesKey"):
                pass
            if hasattr(column, "related_name"):
                pass
            if hasattr(column, "relTo"):
                pass
            if hasattr(column, "unique"):
                pass
            if hasattr(column, "values"):
                pass
            if hasattr(column, "verbose_name"):
                pass

            columns_with_types.append(coltype)
            columns_names.append(colname)

        tables_with_columns[tablename_case] = {
            "columns_with_types": columns_with_types,
            "columns_names": columns_names,
            "table_attributes": table_attributes,
        }
    return tables_with_columns


def kolom_as_params(table, exclude=""):
    """
    exclude
    """
    columns = [f"{col.label}: {col.type}" for col in table.children]
    if exclude:
        columns = [
            f"{col.label}: {col.type}" for col in table.children if col.label != exclude
        ]
    return ", ".join(columns)


def kolom_as_args(table, exclude=None):
    columns = [col.label for col in table.children]
    if exclude:
        columns = [col.label for col in table.children if col.label != exclude]
    return ", ".join(columns)


def jenis_kolom(jenis, backend="django"):
    if jenis not in type_mapper:
        return jenis
    pertama = type_mapper.get(jenis)
    if backend not in pertama:
        return jenis
    return pertama.get(backend, jenis)


def tab_real(num=1, tab="\t"):
    return num * tab


def tab(num=1, space=" ", tab="\t", use_space=True, space_size=TAB_SPACE_MULT):
    """
    utk space:
    tab='\n'
    atau
    use_space=True (default)
    """
    if use_space:
        return num * space * space_size
    else:
        return num * tab


def tabber(num_tab=1, use_tab=True, space_size=2):
    tabber = (
        tab(num=num_tab, use_space=False)
        if use_tab
        else tab(num=num_tab, space=space_size * " ", use_space=True)
    )
    return tabber


def tab_tab(num=1):
    return tab(num=num, use_space=False)


def tab_space(num=1, space_size=2):
    return tab(num=num, use_space=True, space_size=space_size)


def tabify_content(content, self_tab=tab(), num_tab=1):
    tabify = [num_tab * self_tab + item for item in content.splitlines()]
    return "\n".join(tabify)


def tabify_contentlist(content, self_tab=tab(), num_tab=1):
    tabify = [num_tab * self_tab + item for item in content]
    return "\n".join(tabify)


def append_entry(filepath_output, header, body):
    """
    /apps/{tablename}/models.py
    """
    start = "--%"
    end = "--#"
    # header = f'/apps/{tablename}/models.py'
    entry_model = f"\n{start} {header}\n" + body + f"\n{end}\n"
    append_file(filepath_output, entry_model)
    return entry_model


def gen_template_db_init(
    RootNode, return_backend=False, print_info=False, use_real_tab=False
):
    dbvalues = {}
    dblines = []
    dbinfo = RootNode
    if hasattr(dbinfo, "username"):
        dbvalues["username"] = dbinfo.username
        dblines.append(f"%__TEMPLATE_DBUSER={dbinfo.username}")

    if hasattr(dbinfo, "password"):
        dbvalues["password"] = dbinfo.password
        dblines.append(f"%__TEMPLATE_DBPASS={dbinfo.password}")

    if hasattr(dbinfo, "host"):
        dbvalues["host"] = dbinfo.host
        dblines.append(f"%__TEMPLATE_DBHOST={dbinfo.host}")

    if hasattr(dbinfo, "port"):
        dbvalues["port"] = dbinfo.port
        dblines.append(f"%__TEMPLATE_DBPORT={dbinfo.port}")

    if hasattr(dbinfo, "dbname"):
        dbvalues["dbname"] = dbinfo.dbname
        dblines.append(f"%__TEMPLATE_DBNAME={dbinfo.dbname}")

    db_backend = "sqlite"
    if (
        "host" in dbvalues
        or "port" in dbvalues
        or "username" in dbvalues
        or "password" in dbvalues
    ):
        db_backend = "postgres"

    # %__TEMPLATE_DBUSER=usef
    # %__TEMPLATE_DBPASS=rahasia
    # %__TEMPLATE_DBHOST=gisel.ddns.net
    # %__TEMPLATE_DBPORT=9022
    # %__TEMPLATE_DBNAME=ecomm
    if use_real_tab:
        template_db_init = "\n".join([tab_real(1) + item for item in dblines])
    else:
        template_db_init = "\n".join([tab(1) + item for item in dblines])
    if print_info:
        print("=" * 20, "dblines")
        print(template_db_init)

    if return_backend:
        return template_db_init, db_backend

    return template_db_init


def gen_template_app_init(tables, print_info=False, use_real_tab=False):
    applines = []
    for index, tbl in enumerate(tables, 1):
        appidx = str(index).zfill(2)
        try:
            tablename = tbl.model
        except AttributeError as err:
            # AttributeError: 'AnyNode' object has no attribute 'model'
            print("Ketemu error:", err)
            print(
                'Cek apakah semua kolom kecuali kolom akhir terpisah dg terminator ";".'
            )
            print(traceback.format_exc())
        # perlu utk lower...ini akan jadi nama direktori utk masing2 app
        applines.append(f"%__TEMPLATE_APP{appidx}={tablename.lower()}")

    if use_real_tab:
        template_app_init = "\n".join([tab_real(1) + item for item in applines])
    else:
        template_app_init = "\n".join([tab(1) + item for item in applines])
    if print_info:
        print("=" * 20, "applines")
        print(template_app_init)

    return template_app_init


def generate_app_content(tables, app_content_template, print_info=False):
    contentlines = []
    for index, tbl in enumerate(tables, 1):
        appidx = str(index).zfill(2)
        tablename = tbl.model
        content = app_content_template(appidx, tablename)
        contentlines.append(content)

    # template_app_content = '\n'.join([tab(2)+item for item in contentlines])
    template_app_content = "\n".join(contentlines)
    if print_info:
        print("=" * 20, "contentlines")
        print(template_app_content)

    return template_app_content


def write_mkfile(mkfile_content, filepath_output):
    file_write(filepath_output, mkfile_content)
