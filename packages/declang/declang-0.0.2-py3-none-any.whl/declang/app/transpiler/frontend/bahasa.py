from langutils.langs import base_grammar


declarative_program = """
declarative_program: declarative_element (declarative_element)*

declarative_element: "<" element_name element_config? cdata_text? element_children?

element_name: HURUF_DIGIT
element_config_separator: ","

element_config: "[" element_config_item (element_config_separator element_config_item)* "]"
//  | "$" element_config_item_berslash (element_config_separator element_config_item_berslash)* "$"

//element_config: "/" element_config_item (element_config_separator element_config_item)*
//  | "$" element_config_item_berslash (element_config_separator element_config_item_berslash)*


element_config_item: HURUF_DIGIT  -> item_key_value_boolean
  | item_key "=" item_value       -> item_key_value



//element_config_item_berslash: HURUF_DIGIT  -> item_key_value_boolean
//  | item_key "=" item_value       -> item_key_value
//  | item_key "=" item_value_berslash       -> item_key_value_berslash

element_children: "(" declarative_program ")"

item_key: HURUF_DIGIT
// item value hrs bisa terima:
// ' " { } ( ) [ ] / @ : ;
// <Route path="/@:username/favorites" component={ProfileFavorites} />

item_value: HURUF_NILAI
//  | "'" HURUF_NILAI_BERSPASI "'" -> diapit_sq
//  | "\\"" HURUF_NILAI_BERSPASI "\\"" -> diapit_dq

//item_value_berslash: HURUF_NILAI_BERSLASH

// cdata_text: HURUF_CDATA
cdata_text: "|" HURUF_CDATA

transformer: transform_value (transform_value)*
transform_value: "'" -> tx_single
| "\\"" -> tx_double
| "'d" -> tx_double
| "'c" -> tx_braces
| "'k" -> tx_brackets
| "'p" -> tx_parentheses
"""

huruf_berbeda = """
HURUF_CDATA: ("_"|LETTER|DIGIT) 	("_"|LETTER|DIGIT|"."|" "|";"|":"|"+"|"-"|","|"!")*

HURUF_NILAI: ("_"|LETTER|DIGIT|"\\""|"{"|"."|"'") 	("_"|LETTER|DIGIT|"."|"\\""|"'"|"`"|"{"|"}"|"="|"<"|">"|"!"|"("|")"|" "|":"|"/"|"-"|"?")*

HURUF_NILAI_BERSLASH: ("_"|LETTER|DIGIT|"\\""|"{") 	("_"|LETTER|DIGIT|"."|"\\""|"'"|"`"|"{"|"}"|"="|"<"|">"|"!"|"("|")"|" "|"/")*
HURUF_NILAI_BERSPASI: ("_"|LETTER|DIGIT|"\\""|"{") 	("_"|LETTER|DIGIT|"."|"`"|"{"|"}"|"("|")"|"="|">"|" ")*
HURUF_NON_OPEN: ("_"|LETTER|DIGIT) 	("_"|LETTER|DIGIT|"."|","|" "|"+"|"="|"-"|"_"|"@"|"#"|"$"|"%"|"^"|"&"|"*")*
HURUF_KODE_FRONTEND: ("_"|LETTER|DIGIT|"\\""|"{"|"<") 	("_"|LETTER|DIGIT|"."|"\\""|"'"|"`"|"{"|"}"|"="|"<"|">"|"!"|"("|")"|" "|"/")*
"""

huruf = """
HURUF_DIGIT: ("_"|LETTER|DIGIT) 	("_"|LETTER|DIGIT|".")*
"""

# <PersistGate /loading={<FullScreen Berspasi>},persistor={persistor}/
# <PersistGate $loading={<FullScreen />},persistor={persistor}$
# <PersistGate $loading={<FullScreen />},persistor={persistor}$bertulisan sblm children
# <a<b<c
# <a<b<c(<d<e)
# <a/disabled=true,onClick={()=>Mycomponent}/(<b)
# <a(<b<c(<e(<g(<i(<j<k/disabled/<l))<h)<f)<d)
# <a/disabled, nama=kuda, onClick={handleMe}/
# <a/disabled/ini adlh tulisanku untukmu
# <a/disabled/ini adlh tulisanku untukmu(<b(<c))

bahasa = f"""
{declarative_program}

{huruf_berbeda}

{huruf}

{base_grammar}
"""
