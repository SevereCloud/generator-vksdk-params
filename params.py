import shutil
import os

TYPES = {
    "integer": "int",
    "number": "float64",
    "string": "string",
    "boolean": "bool"
}

TYPES_TEST = {
    "integer": "1",
    "number": "1.1",
    "string": '"text"',
    "boolean": "true"
}


def test_type_value(parameter):
    type_value = TYPES_TEST.get(parameter.get("type"))

    if parameter.get("type") == "array":
        type_items = TYPES.get(parameter["items"].get("type"))
        type_items_value = TYPES_TEST.get(parameter["items"].get("type"))
        if not type_items:
            type_items = "string"
            type_items_value = '"test"'

        type_value = "[]" + type_items + "{" + type_items_value + "}"

    return type_value


def camel(s):
    for i in range(len(s)):
        if s[i] in ["id", "html", "url", "sid", "aid", "uid", "api", "ip", "guid"]:
            s[i] = s[i].upper()
        s[i] = s[i][0].upper() + s[i][1:]
        if s[i] == "Ids":
            s[i] = "IDs"

    return s


def name_builder(method: str):
    s = method.split('.')
    s[1] = s[1].replace("Id", "ID")

    return "".join(camel(s))


def name_params(param: str):
    s = param.split('_')

    return "".join(camel(s))


def handler(schema, build_folder, version):
    folder_path = build_folder + '/params'

    if os.path.exists(folder_path):
        shutil.rmtree(folder_path, ignore_errors=True)
    os.makedirs(folder_path)

    not_empty = []

    for method in schema["methods"]:
        if not method.get('parameters'):
            continue
        if len(method["parameters"]) == 0:
            continue

        file_name = method["name"].split('.')[0]
        file_path = f'{folder_path}/{file_name}.go'

        with open(file_path, 'a') as f:

            if file_name not in not_empty:
                # first line
                f.write(
                    'package params // import "github.com/SevereCloud/vksdk/api/params"\n')
                f.write('\n')
                f.write('import (\n')
                f.write('\t"github.com/SevereCloud/vksdk/api"\n')
                f.write(')\n')

                not_empty.append(file_name)

            # Комментарии
            name_b = name_builder(method["name"]) + "Bulder"

            f.write('\n')
            f.write(f'// {name_b} builder\n')

            if method.get('description'):
                f.write('//\n')
                f.write(f'// {method["description"]}\n')

            f.write('//\n')
            f.write(f'// https://vk.com/dev/{method["name"]}\n')

            # Тип
            f.write(f'type {name_b} ')
            f.write('struct {\n')
            f.write('\tapi.Params\n')
            f.write('}\n\n')

            # функция
            f.write(f'// New{name_b} func\n')
            f.write(f'func New{name_b}() *{name_b} ')
            f.write('{\n')
            f.write(f'\treturn &{name_b}')
            f.write('{api.Params{}}\n')
            f.write('}\n')

            # Параметры
            for parameter in method["parameters"]:
                f.write('\n')
                name_p = name_params(parameter["name"])

                type_value = TYPES.get(parameter.get("type"))
                if parameter.get("type") == "array":
                    type_items = TYPES.get(parameter["items"].get("type"))
                    if not type_items:
                        type_items = "string"
                    type_value = "[]" + type_items

                desc = "parameter"
                if parameter.get("description"):
                    desc = parameter.get("description")
                f.write(f'// {name_p} {desc}\n')

                f.write(f'func (b *{name_b}) {name_p}(v {type_value}) ')
                f.write('{\n')
                f.write(f'\tb.Params["{parameter["name"]}"] = v\n')
                f.write('}\n')

        file_name = method["name"].split('.')[0] + "_test"
        file_path = f'{folder_path}/{file_name}.go'

        with open(file_path, 'a') as f:

            if file_name not in not_empty:
                # first line
                f.write('package params_test\n')
                f.write('\n')
                f.write('import (\n')
                f.write('\t"testing"\n\n')
                f.write('\t"github.com/SevereCloud/vksdk/api/params"\n')
                f.write('\t"github.com/stretchr/testify/assert"\n')
                f.write(')\n')

                not_empty.append(file_name)

            name_b = name_builder(method["name"]) + "Bulder"

            # Тест
            f.write('\n')
            f.write(f'func Test{name_b}(t *testing.T) ')
            f.write('{\n')
            f.write(f'\tb := params.New{name_b}()\n\n')

            # Параметры
            for parameter in method["parameters"]:
                name_p = name_params(parameter["name"])
                type_value = test_type_value(parameter)

                f.write(f'\tb.{name_p}({type_value})\n')
            f.write('\n')

            for parameter in method["parameters"]:
                type_value = test_type_value(parameter)

                f.write(
                    f'\tassert.Equal(t, b.Params["{parameter["name"]}"], {type_value})\n')

            f.write('}\n')
