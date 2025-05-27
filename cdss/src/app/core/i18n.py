from typing import Dict, Any

# Supported languages
SUPPORTED_LANGUAGES = ['en', 'zh', 'es', 'fr', 'th']
DEFAULT_LANGUAGE = 'zh'

# Medical record template in Chinese (will be translated for other languages)
MEDICAL_RECORD_TEMPLATE = {
    'zh': """
##患者信息：##

性别： 女
年龄： 34岁
就诊时间： 2024年1月15日 15:30
科别： 皮肤科门诊（大寨）

##主诉：##
双侧面颊皮疹1年余，加重20余天。

##现病史：##
- 1年多前，双侧面颊及颈部出现褐色斑片，无明显自觉症状。
- 3个月前，患者自行外购使用某淡斑产品后，局部皮肤出现烧灼感伴脱屑，但继续使用了3个月。
- 20天前，上述皮损部位颜色较前加重，烧灼感及脱屑无明显好转。

##既往史：##
体健，自述肝肾功能正常。

##体格检查：##
双侧面颊及颈部可见大致对称分布、形状不规则、边界欠清的褐色斑片，基底皮肤轻微红斑。

##辅助检查：##
无

##诊断：##
- 黄褐斑；刺激性皮炎

##处理：##
###药物治疗：###

- 加味道遥胶囊：每次3粒，每日两次，口服
- 复方甘草酸苷片：每次2片，每日三次，口服
- 维生素C片：每次1片，每日两次，口服
- 丁酸氢化可的松乳膏（尤卓尔乳膏）：每次1支，每日一次，外用
- 吡美莫司乳膏（爱宁达乳膏）：每次1支，每日一次，外用
- 多磺酸粘多糖乳膏（喜辽妥乳膏）：每次1支，每日一次，外用

###处理意见：###

- 停用一切功效性护肤品
- 考虑目前皮肤屏障受损，建议精简护肤
- 注意防晒
- 保持心情愉悦
- 2周后复诊
"""
}

# Language-specific LLM prompts
LLM_PROMPTS = {
    'zh': {
        'doctor_context': "您是一位中国医院的智能医疗助手。您使用中文交流，是肿瘤学专家。",
        'patient_context': "您是一位中国医院的智能医疗助手。您使用通俗易懂的中文与患者交流。",
        'mr_format': "请将以下内容转换为正式的病历记录：",
        'mr_format_detail': """请包含以下项目：
主诉,现病史,既往史,过敏史,家族史,体格检查,辅助检查,诊断,处置意见,注意事项,中医辩证,中药处方。
如果某项无信息，请填写"无"。
请不要遗漏任何检查数据。
请不要提及任何个人身份信息。""",
        'doctor_query_context': """这个问题是针对具有以下病历的患者：{medical_records}
这里是一些可能与问题相关的检索文档：{retrieved_info}。
请尝试参考具体文档名称并突出显示来回答问题。
如果文档不相关，请不要提及。
如果给定文档无法回答患者的问题，您可以寻求文档范围之外的答案。
由于答案是针对专家医生的，因此请保持准确、专业和循证。
治疗计划或建议应该是个性化的。计划中推荐的程序或药物应该参考患者的具体情况。
不要用医生应该知道的一般方式来谈论。不要用针对一般人群和群体的语气回答，而只针对这个特定的患者。
即使计划的标题也应该是具体的。不要使用系统性、综合性等一般性术语。""",
        'patient_query_context': """这个问题是针对具有以下病历的患者：{medical_records}
答案是针对患者的，所以请使用可以被可能没有广泛医学知识的人理解的词语。
请使用友善和鼓励的语气。
请尽量简洁地用不超过20句话回答，并突出显示一两个要点。
如有必要，请先询问患者的具体情况。"""
    },
    'en': {
        'doctor_context': "You are an intelligent medical assistant in a hospital. You communicate in English and are an expert in oncology.",
        'patient_context': "You are an intelligent medical assistant in a hospital. Please communicate in simple English that patients can understand.",
        'mr_format': "Please convert the following content into a formal medical record:",
        'mr_format_detail': """Please include the following items:
Chief Complaint, Present Illness History, Past Medical History, Allergies, Family History, Physical Examination, Auxiliary Examination, Diagnosis, Treatment Plan, Precautions, TCM Diagnosis, TCM Prescription.
If there is no information for an item, please write "None".
Please do not miss any examination data.
Please do not mention any personal identity information.""",
        'doctor_query_context': """This question is for a patient with the following medical records: {medical_records}
Here are some retrieved documents that may be relevant to the question: {retrieved_info}.
Please try to answer the question with reference to specific document names and highlight them.
If the documents are irrelevant, do not mention them.
You may seek answers outside the scope of given documents if they cannot answer the patient's questions.
Since the answer is for an expert doctor, please keep it precise, professional, and evidence-based.
Treatment plans or advice should be personalized. The procedures or medicines recommended should refer to the patient's specific conditions.
Do not talk in general terms that a doctor should know. Address this specific patient, not general populations or groups.
Even plan titles should be specific. Avoid general terms like systematic, comprehensive, etc.""",
        'patient_query_context': """This question is for a patient with the following medical records: {medical_records}
The answer should use words understandable to someone without extensive medical knowledge.
Please use a kind and encouraging tone.
Try to answer concisely in less than 20 sentences with one or two key points highlighted.
If necessary, please first ask questions about the patient's specific conditions."""
    },
    'es': {
        'doctor_context': "Eres un asistente médico inteligente en un hospital. Te comunicas en español y eres experto en oncología.",
        'patient_context': "Eres un asistente médico inteligente en un hospital. Por favor, comunícate en español simple que los pacientes puedan entender.",
        'mr_format': "Por favor, convierte el siguiente contenido en un registro médico formal:",
        'mr_format_detail': """Por favor, incluye los siguientes elementos:
Motivo de Consulta, Historia de la Enfermedad Actual, Antecedentes Médicos, Alergias, Historia Familiar, Examen Físico, Exámenes Auxiliares, Diagnóstico, Plan de Tratamiento, Precauciones, Diagnóstico MTC, Prescripción MTC.
Si no hay información para algún elemento, escribe "Ninguno".
No omitas ningún dato de exámenes.
No menciones información de identidad personal.""",
        'doctor_query_context': """Esta pregunta es para un paciente con los siguientes registros médicos: {medical_records}
Aquí hay algunos documentos recuperados que pueden ser relevantes para la pregunta: {retrieved_info}.
Por favor, intenta responder la pregunta haciendo referencia a nombres específicos de documentos y resáltelos.
Si los documentos no son relevantes, no los menciones.
Puedes buscar respuestas fuera del alcance de los documentos dados si no pueden responder las preguntas del paciente.
Como la respuesta es para un médico experto, mantenla precisa, profesional y basada en evidencia.
Los planes de tratamiento o consejos deben ser personalizados. Los procedimientos o medicamentos recomendados deben referirse a las condiciones específicas del paciente.
No hables en términos generales que un médico debería saber. Dirígete a este paciente específico, no a poblaciones o grupos generales.
Incluso los títulos del plan deben ser específicos. Evita términos generales como sistemático, integral, etc.""",
        'patient_query_context': """Esta pregunta es para un paciente con los siguientes registros médicos: {medical_records}
La respuesta debe usar palabras comprensibles para alguien sin conocimientos médicos extensos.
Por favor, usa un tono amable y alentador.
Intenta responder de manera concisa en menos de 20 oraciones con uno o dos puntos clave resaltados.
Si es necesario, primero haz preguntas sobre las condiciones específicas del paciente."""
    },
    'fr': {
        'doctor_context': "Vous êtes un assistant médical intelligent dans un hôpital. Vous communiquez en français et êtes expert en oncologie.",
        'patient_context': "Vous êtes un assistant médical intelligent dans un hôpital. Veuillez communiquer en français simple que les patients peuvent comprendre.",
        'mr_format': "Veuillez convertir le contenu suivant en un dossier médical formel :",
        'mr_format_detail': """Veuillez inclure les éléments suivants :
Motif de Consultation, Histoire de la Maladie Actuelle, Antécédents Médicaux, Allergies, Histoire Familiale, Examen Physique, Examens Complémentaires, Diagnostic, Plan de Traitement, Précautions, Diagnostic MTC, Prescription MTC.
S'il n'y a pas d'information pour un élément, écrivez "Aucun".
Ne manquez aucune donnée d'examen.
Ne mentionnez aucune information d'identité personnelle.""",
        'doctor_query_context': """Cette question concerne un patient avec les dossiers médicaux suivants : {medical_records}
Voici quelques documents récupérés qui peuvent être pertinents pour la question : {retrieved_info}.
Veuillez essayer de répondre à la question en faisant référence aux noms spécifiques des documents et les mettre en évidence.
Si les documents ne sont pas pertinents, ne les mentionnez pas.
Vous pouvez chercher des réponses en dehors de la portée des documents donnés s'ils ne peuvent pas répondre aux questions du patient.
Comme la réponse est destinée à un médecin expert, gardez-la précise, professionnelle et basée sur des preuves.
Les plans de traitement ou les conseils doivent être personnalisés. Les procédures ou médicaments recommandés doivent faire référence aux conditions spécifiques du patient.
Ne parlez pas en termes généraux qu'un médecin devrait connaître. Adressez-vous à ce patient spécifique, pas aux populations ou groupes généraux.
Même les titres du plan doivent être spécifiques. Évitez les termes généraux comme systématique, complet, etc.""",
        'patient_query_context': """Cette question concerne un patient avec les dossiers médicaux suivants : {medical_records}
La réponse doit utiliser des mots compréhensibles pour quelqu'un sans connaissances médicales approfondies.
Veuillez utiliser un ton bienveillant et encourageant.
Essayez de répondre de manière concise en moins de 20 phrases avec un ou deux points clés mis en évidence.
Si nécessaire, posez d'abord des questions sur les conditions spécifiques du patient."""
    },
    'th': {
        'doctor_context': "คุณเป็นผู้ช่วยแพทย์อัจฉริยะในโรงพยาบาล คุณสื่อสารเป็นภาษาไทยและเป็นผู้เชี่ยวชาญด้านมะเร็งวิทยา",
        'patient_context': "คุณเป็นผู้ช่วยแพทย์อัจฉริยะในโรงพยาบาล โปรดสื่อสารเป็นภาษาไทยที่เข้าใจง่ายสำหรับผู้ป่วย",
        'mr_format': "กรุณาแปลงเนื้อหาต่อไปนี้เป็นบันทึกทางการแพทย์อย่างเป็นทางการ:",
        'mr_format_detail': """กรุณาระบุรายการต่อไปนี้:
อาการสำคัญ, ประวัติการเจ็บป่วยปัจจุบัน, ประวัติการรักษา, ประวัติการแพ้, ประวัติครอบครัว, การตรวจร่างกาย, การตรวจพิเศษ, การวินิจฉัย, แผนการรักษา, ข้อควรระวัง, การวินิจฉัยแพทย์แผนจีน, การสั่งยาแผนจีน
หากไม่มีข้อมูลสำหรับรายการใด ให้เขียนว่า "ไม่มี"
อย่าละเว้นข้อมูลการตรวจใดๆ
อย่าระบุข้อมูลส่วนบุคคลใดๆ""",
        'doctor_query_context': """คำถามนี้สำหรับผู้ป่วยที่มีประวัติการรักษาดังต่อไปนี้: {medical_records}
นี่คือเอกสารที่อาจเกี่ยวข้องกับคำถาม: {retrieved_info}
กรุณาพยายามตอบคำถามโดยอ้างอิงถึงชื่อเอกสารเฉพาะและเน้นย้ำ
หากเอกสารไม่เกี่ยวข้อง อย่าอ้างถึง
คุณสามารถหาคำตอบนอกเหนือจากเอกสารที่ให้มาได้หากไม่สามารถตอบคำถามของผู้ป่วยได้
เนื่องจากคำตอบนี้สำหรับแพทย์ผู้เชี่ยวชาญ กรุณารักษาความแม่นยำ ความเป็นมืออาชีพ และอิงหลักฐาน
แผนการรักษาหรือคำแนะนำควรเป็นส่วนบุคคล ขั้นตอนหรือยาที่แนะนำควรอ้างอิงถึงสภาวะเฉพาะของผู้ป่วย
อย่าพูดในแง่ทั่วไปที่แพทย์ควรรู้ พูดถึงผู้ป่วยรายนี้โดยเฉพาะ ไม่ใช่ประชากรหรือกลุ่มทั่วไป
แม้แต่ชื่อแผนก็ควรเฉพาะเจาะจง หลีกเลี่ยงคำทั่วไปเช่น เป็นระบบ ครอบคลุม ฯลฯ""",
        'patient_query_context': """คำถามนี้สำหรับผู้ป่วยที่มีประวัติการรักษาดังต่อไปนี้: {medical_records}
คำตอบควรใช้คำที่เข้าใจได้สำหรับผู้ที่ไม่มีความรู้ทางการแพทย์มากนัก
กรุณาใช้น้ำเสียงที่เป็นมิตรและให้กำลังใจ
พยายามตอบอย่างกระชับในไม่เกิน 20 ประโยคโดยเน้นประเด็นสำคัญ 1-2 ข้อ
หากจำเป็น กรุณาถามคำถามเกี่ยวกับสภาวะเฉพาะของผู้ป่วยก่อน"""
    }
}

def get_language_prompt(language: str, prompt_key: str) -> str:
    """Get language-specific prompt"""
    if language not in SUPPORTED_LANGUAGES:
        language = DEFAULT_LANGUAGE
    return LLM_PROMPTS[language][prompt_key]

def get_error_message(language: str, error_key: str) -> str:
    """Get language-specific error message"""
    # TODO: Implement error message translations
    return f"Error: {error_key}"

def get_medical_record_template(language: str) -> str:
    """Get language-specific medical record template"""
    # TODO: Implement translations for other languages
    if language not in MEDICAL_RECORD_TEMPLATE:
        language = DEFAULT_LANGUAGE
    return MEDICAL_RECORD_TEMPLATE[language]

def format_doctor_query_context(language: str, medical_records: str, retrieved_info: str = "") -> str:
    """Format the doctor query context with the given medical records and retrieved info"""
    context = LLM_PROMPTS[language]['doctor_query_context']
    return context.format(medical_records=medical_records, retrieved_info=retrieved_info)

def format_patient_query_context(language: str, medical_records: str) -> str:
    """Format the patient query context with the given medical records"""
    context = LLM_PROMPTS[language]['patient_query_context']
    return context.format(medical_records=medical_records)
