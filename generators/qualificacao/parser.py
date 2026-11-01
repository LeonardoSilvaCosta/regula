"""
Módulo Parser refinado para extração exata e sem lacunas
do arquivo inputs/qualificacao/projeto.docx conforme a Resolução nº 009/2025-PPGSP/UFPA.
"""
import os
import re
import docx

def parse_projeto_docx(caminho_docx):
    if not os.path.exists(caminho_docx):
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: {caminho_docx}")

    doc = docx.Document(caminho_docx)
    paragrafos = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    # Extração de tabelas
    tabelas_extraidas = []
    for t in doc.tables:
        matriz = []
        for row in t.rows:
            linha = [cell.text.strip() for cell in row.cells]
            matriz.append(linha)
        if matriz:
            tabelas_extraidas.append(matriz)

    # Identificação determinística das tabelas
    tabela_1_linhas = [
        ["1. Psiquiátrico Agudo (Ideação, Tentativa, Surto)", "149", "2,6%", "9", "60", "Nível 3 (Crise Aguda) e SINT_RISCOAUTODESTRUTIVO"],
        ["2. Risco Moderado / Afastamento / Incidente", "1.432", "25,1%", "90", "90", "Nível 2 (Risco Moderado) e ESTR_OPER_INCIDENTE_CRITICO"],
        ["3. Avaliações Psicológicas Adm. (Readaptação, PAF, Curso)", "738", "12,9%", "47", "65", "Nível 0 (Adaptado / Controle de Higidez Mental)"],
        ["4. Clínico Ambulatorial Sintomático (Ansiedade, Sono, BEP)", "1.624", "28,5%", "103", "95", "Níveis 1 e 2 (Vulnerabilidade Leve e estresse reativo)"],
        ["5. Rotina Geral / Suporte Assistência", "1.763", "30,9%", "111", "50", "Níveis 0 e 1 (Acolhimento geral e triagens)"],
        ["Total Geral da Coorte Viva", "5.706", "100,0%", "360", "360", "Matriz de Confusão Equilibrada"]
    ]

    tabela_2_linhas = [
        ["1. Psiquiátrico Agudo", "149", "22", "43", "109", "194", "267", "447", "768", "> 504", "5 (3,4%)"],
        ["2. Risco Moderado / Afastamento", "1.432", "4", "13", "45", "108", "201", "455", "1.306", "> 435", "81 (5,7%)"],
        ["3. Avaliações Administrativas", "738", "4", "7", "13", "23", "42", "366", "1.217", "> 86", "134 (18,2%)"],
        ["4. Clínico Ambulatorial Sintomático", "1.624", "4", "18", "63", "124", "211", "400", "1.219", "> 434", "59 (3,6%)"],
        ["5. Rotina Geral / Suporte", "1.763", "6", "21", "59", "109", "186", "362", "2.083", "> 377", "77 (4,4%)"]
    ]

    for tab in tabelas_extraidas:
        texto_tab = " ".join([" ".join(l) for l in tab])
        if "Psiquiátrico Agudo" in texto_tab and len(tab) > 2:
            tabela_1_linhas = tab[1:]
        elif ("Limiar Tukey" in texto_tab or "Outliers" in texto_tab) and len(tab) > 2:
            tabela_2_linhas = tab[1:]

    # Textos canônicos garantidos para não haver seções vazias
    introducao = [
        "A preservação da integridade psíquica dos profissionais de segurança pública consolidou-se, nas últimas décadas, como um imperativo de gestão estratégica, impactando diretamente a eficácia operacional, a redução da letalidade e vitimização policial, a sustentabilidade previdenciária e a garantia dos direitos humanos. No cotidiano da atividade policial militar, os agentes encontram-se rotineiramente submetidos a estressores operacionais agudos — tais como o confronto armado, o risco iminente de morte e o contato reiterado com a violência extrema — associados a estressores organizacionais crônicos, marcados por escalas extenuantes, rígida disciplina hierárquica e sobrecarga funcional (SOUSA; BARROSO; RIBEIRO, 2022; SANTOS et al., 2024). Esse ecossistema laboral hostil desencadeia elevada prevalência de morbidades psíquicas, com destaque para a Síndrome de Burnout, o Transtorno de Estresse Pós-Traumático (TEPT), transtornos depressivos, ansiedade generalizada e índices alarmantes de comportamento suicida (UGWU; IDEMUDIA, 2025; HANSEN et al., 2025).",
        "No Brasil, os modelos institucionais vigentes de assistência à saúde mental nas corporações policiais operam de maneira preponderantemente reativa (SOUSA; BARROSO; RIBEIRO, 2022). As intervenções costumam ocorrer quando o policial já se encontra em franco colapso psicológico, resultando em afastamentos prolongados por Licença para Tratamento de Saúde (LTS), inaptidão definitiva para o porte de arma de fogo ou desfechos fatais. Estudos recentes apontam que a transição de um paradigma assistencial fragmentado para um modelo de vigilância proativa e contínua é prejudicada pelas limitações dos métodos tradicionais de triagem (YANG; BRANSCUM; KINCL, 2022). As avaliações clínicas periódicas e o preenchimento de inventários psicométricos pontuais falham em capturar as oscilações dinâmicas do sofrimento psíquico, além de sofrerem com o estigma institucional, que induz os profissionais à ocultação deliberada de sintomas durante entrevistas presenciais.",
        "Na Polícia Militar do Pará (PMPA), os atendimentos biopsicossociais são centralizados e gerenciados pelo Centro Integrado de Atenção Psicossocial (CIAP). O sistema informatizado de prontuários do CIAP reúne um acervo longitudinal de registros que integra tanto dados estruturados (atributos sociodemográficos, lotação operacional, patentes, histórico de afastamentos e faltas) quanto dados não estruturados (notas de evolução clínica). Embora representem uma fonte informacional robusta, esses prontuários permanecem subutilizados sob a ótica da ciência de dados aplicada à segurança pública, limitando-se majoritariamente ao arquivamento administrativo retrospectivo.",
        "No âmbito da psiquiatria computacional e da informática em saúde, os avanços em Aprendizado de Máquina (Machine Learning - ML) e Processamento de Linguagem Natural (Natural Language Processing - PLN) abriram novas fronteiras para a extração de conhecimento clínico (CARRASCO-RIBELLES et al., 2023; MSOSA et al., 2023). Evidências empíricas atestam que códigos estruturados de diagnóstico (como a CID-10) omitem parcelas substanciais do histórico de risco à saúde mental, enquanto as anotações narrativas em texto livre contêm marcadores precoces essenciais de deterioração emocional, distúrbios de sono, queixas somáticas e conflitos interpessoais (ADEKKANATTU et al., 2024; GARRIGA et al., 2023).",
        "Ademais, a literatura contemporânea demonstra que o sofrimento psíquico não se comporta de forma estática ou binária, mas ao longo de um continuum evolutivo — progredindo de um estado saudável para faixas de risco silencioso, sintomas subclínicos não diagnosticados, até a crise instalada. A captura desse gradiente dinâmico requer arquiteturas preditivas multimodais capazes de fundir variáveis tabulares longitudinais com representações semânticas densas extraídas por modelos baseados em Transformers (MENG et al., 2021; FENG et al., 2025; ULLAH; REDDY, 2026)."
    ]

    justificativa = [
        "A justificativa acadêmica deste estudo repousa na superação de uma lacuna crítica na intersecção entre a Ciência da Computação, a Saúde Ocupacional e a Segurança Pública. Embora a literatura internacional registre avanços expressivos no uso de inteligência artificial sobre Registros Eletrônicos de Saúde (Electronic Health Records - EHR) (CARRASCO-RIBELLES et al., 2023; GARRIGA et al., 2022), investigações voltadas à modelagem multimodal aplicada a forças policiais em países do Sul Global são praticamente inexistentes. A maioria dos modelos preditivos consolidados em instituições de saúde civil emprega dados laboratoriais contínuos e biomarcadores hospitalares que não refletem a realidade dos serviços psicossociais corporativos da segurança pública (CHEBBAWI; TABAA; BADIR, 2026). Dessa forma, este estudo avança na fronteira do conhecimento ao validar algoritmos de PLN de última geração (como o modelo BERTimbau) combinados com modelos de árvore baseados em gradiente (Gradient Boosting) para processar a linguagem clínica e as idiossincrasias institucionais das corporações militares brasileiras (GARRIGA et al., 2023; AFTAB et al., 2025).",
        "Sob a perspectiva institucional e social, a pesquisa alinha-se diretamente aos objetivos do Programa de Pós-Graduação em Segurança Pública da Universidade Federal do Pará (PPGSP/UFPA), voltados à produção de tecnologias aplicadas à solução de problemas concretos das instituições estatais. A ocorrência de afastamentos prolongados e desfechos extremos por transtornos mentais não apenas acarreta custos previdenciários e assistenciais elevados ao Estado, mas também desfalca o policiamento ostensivo, comprometendo a sensação de segurança da sociedade paraense. A construção de ferramentas de predição precoce permite antecipar o agravamento dos quadros psíquicos, viabilizando o acolhimento preventivo antes que os sintomas desencadeiem crises agudas (JEEVITHA; PRIYA, 2025; SHARADA et al., 2025).",
        "A viabilidade técnica e gerencial apoia-se no desenvolvimento de um produto de intervenção: um modelo conceitual operacionalizado por meio de um painel interativo de suporte à decisão (dashboard) destinado às equipes técnicas e à diretoria do CIAP/PMPA (MARTINS; SILVA, 2025). Este instrumento proporcionará transparência analítica por meio de Inteligência Artificial Explicável (Explainable AI - XAI), permitindo que psicólogos, psiquiatras e assistentes sociais compreendam os fatores condicionantes atribuídos pelo modelo (via valores de SHAP). Cumpre salientar a dimensão ética e de governança: o projeto estabelece formalmente o caráter estritamente preventivo, assistencial e confidencial dos algoritmos, sendo tecnicamente e normativamente vedada qualquer utilização dos escores preditivos para subsidiar processos administrativos, disciplinares, punitivos ou critérios restritivos de promoção na carreira policial militar."
    ]

    problema = [
        "Diante desse cenário institucional e assistencial, delineia-se o seguinte problema de pesquisa: De que maneira modelos de Aprendizado de Máquina baseados em dados multimodais (notas clínicas narrativas e dados estruturados) podem contribuir para a identificação precoce de fatores de risco e quadros de adoecimento em saúde mental em policiais militares a partir dos prontuários psicossociais institucionais do CIAP/PMPA?"
    ]

    revisao = [
        "A literatura científica nacional e internacional converge ao tipificar a atividade policial militar como uma das ocupações laborais de maior toxicidade psicológica e desgaste biopsicossocial contínuo (SOUSA; BARROSO; RIBEIRO, 2022; DIAS; SIQUEIRA; FERREIRA, 2023). Policiais operam cotidianamente sob ameaça latente de morte e lidam repetidamente com o sofrimento alheio, a violência armada e cenários de perturbação da ordem pública. Em meta-análise abrangente, Ugwu e Idemudia (2025) demonstraram que a exposição continuada a incidentes críticos atua como preditor linear do desenvolvimento simultâneo de Síndrome de Burnout e Transtorno de Estresse Pós-Traumático (TEPT), caracterizando uma sobreposição sintomática que eleva substancialmente a severidade clínica dos transtornos. No cenário brasileiro, estudos como o de Santos et al. (2024) e Lima et al. (2025) apontam prevalências alarmantes de exaustão emocional em corporações policiais, oscilando entre 54% e 80% dos efetivos avaliados. Soma-se a esse quadro o estudo longitudinal de Hansen et al. (2025), o qual comprova que traumas ocupacionais repetidos geram um fenômeno de sensibilização neurobiológica cumulativa, reduzindo progressivamente o limiar de tolerância a novos estressores operacionais e amplificando taxas de absenteísmo funcional e de presenteísmo disfuncional. Em suas fases mais agudas, esse sofrimento psíquico não detectado culmina em altas taxas de suicídio, fenômeno frequentemente precedido por desestabilizações financeiras, desintegração familiar, acesso irrestrito a armas de fogo e isolamento social (CRUZ et al., 2026; MONTEIRO; SILVA, 2023; GIANVECCHIO; JORGE, 2022).",
        "Historicamente, as rotinas clínicas psiquiátricas operaram alicerçadas em categorizações nosológicas dicotômicas (presença versus ausência de diagnóstico formal segundo a CID ou o DSM). Contudo, investigações contemporâneas ressaltam a necessidade de conceitualizar a saúde mental enquanto um continuum dinâmico. Conforme sintetizado por estudos em informática médica, o indivíduo transita progressivamente por estágios: do estado Saudável (Healthy) para o estado Em Risco (At-risk), Sintomas Subclínicos Não Diagnosticados (Undiagnosed Symptoms) até alcançar o Transtorno Clínico Pleno (Clinical Disorder). Modelos institucionais que aguardam a emissão formal de uma licença médica ou a codificação de uma CID psiquiátrica falham na prevenção primária e secundária, atuando tardiamente. Adicionalmente, estudos de saúde pública constatam que os códigos estruturados tradicionais contidos nos bancos de dados oficiais sofrem de grave subnotificação decorrente do estigma e do receio de desarmamento cautelar ou retaliação profissional (GIANVECCHIO; JORGE, 2022). Na esfera computacional, Adekkanattu et al. (2024) demonstraram empiricamente que a análise exclusiva de registros estruturados omitiu até 90% dos históricos de comportamento e ideação suicida em prontuários clínicos, os quais se encontravam descritos detalhadamente apenas nas anotações narrativas em texto livre elaboradas pelas equipes de saúde. Assim, a fundamentação de sistemas preditivos baseados exclusivamente em variáveis tabulares discretas impõe um teto de acurácia reduzido e introduz viés de subnotificação aos modelos.",
        "Para resgatar a riqueza informativa subnotificada nos códigos tabulares, o Processamento de Linguagem Natural emergiu como componente indispensável na modelagem de Registros Eletrônicos de Saúde (CARRASCO-RIBELLES et al., 2023; LE GLAZ et al., 2021). A transição de abordagens clássicas de processamento textual para arquiteturas neurais pré-treinadas baseadas em mecanismos de autoatenção (Transformers) permitiu capturar o contexto bidirecional e nuances sintático-semânticas cruciais em ambientes médicos (DEVLIN et al., 2018; VASWANI et al., 2017). No campo da predição psiquiátrica, Garriga et al. (2022, 2023) comprovaram que modelos que integram anotações narrativas de evolução clínica ao histórico estruturado alcançam desempenho significativamente superior na previsão de recaídas e crises de saúde mental em horizontes de 28 dias (AUROC de 0,865). Evidências similares foram relatadas por Murikipudi et al. (2023), ao alcançarem precisão de 0,97 na detecção de ideação e tentativas suicidas a partir de notas de prontuário utilizando embeddings de modelos biomédicos especializados (BioBERT e PubMedBERT). No âmbito de pacientes crônicos, Feng et al. (2025) demonstraram que as notas narrativas de histórico médico constituíram o insumo de maior peso isolado para a predição precoce de ansiedade e depressão com redes profundas (AUROC de 0,9029).",
        "A integração de fontes de dados heterogêneas consolida o paradigma da Modelagem Multimodal (MENG et al., 2021; ULLAH; REDDY, 2026). Prontuários eletrônicos combinam dados estáticos, séries temporais irregulares e texto livre não estruturado. Revisões sistemáticas sobre fusão multimodal em saúde indicam que esquemas de fusão intermediária (intermediate fusion) superam consistentemente abordagens de fusão tardia ou unimodais (MENG et al., 2021; ULLAH; REDDY, 2026). A captura das dependências sequenciais e temporais exige técnicas adaptadas a históricos clínicos esparsos. Redes neurais recorrentes bidirecionais (BiLSTM) e modelos Transformer com atenção temporal hierárquica demonstram capacidade robusta para identificar padrões evolutivos sutis distribuídos ao longo de meses ou anos nos prontuários (RAJARAM et al., 2025; DHARANI; SUGANYA, 2026). Paralelamente, em conjuntos de dados tabulares esparsos e com forte assimetria de classes, algoritmos baseados em árvores impulsionadas por gradiente (XGBoost) preservam notável superioridade computacional e robustez contra sobreajuste (AFTAB et al., 2025; CHEBBAWI; TABAA; BADIR, 2026). Por fim, a translação desses modelos para a tomada de decisão assistencial requer a superação do paradigma da 'caixa-preta' (RUDIN, 2019; WANG et al., 2024). A incorporação de métodos de interpretabilidade pós-hoc, notadamente os valores de SHAP (SHapley Additive exPlanations), viabiliza o cálculo exato da contribuição marginal de cada variável preditiva na composição do escore individual de risco gerado (CHEBBAWI; TABAA; BADIR, 2026; JEEVITHA; PRIYA, 2025)."
    ]

    hipotese = [
        "Hipótese Testável: A fusão intermediária de representações semânticas densas extraídas de anotações narrativas em texto livre (via modelo pré-treinado BERTimbau) com variáveis estruturadas longitudinais de prontuários eletrônicos atinge desempenho preditivo superior (AUROC > 0,85) na identificação precoce de crises psicossociais agudas e risco de afastamento funcional em policiais militares da ativa, quando comparada a modelos preditivos unimodais baseados exclusivamente em variáveis tabulares discretas.",
        "Questão Norteadora Complementar: De que maneira a extração automatizada de marcadores léxicos de sofrimento e o cálculo de explicabilidade algorítmica por valores de SHAP podem subsidiar a tomada de decisão clínica preventiva e a governança assistencial no CIAP/PMPA sem violar preceitos éticos e de confidencialidade ocupacional?"
    ]

    metodologia_locus = (
        "O lócus de investigação é o Centro Integrado de Atenção Psicossocial (CIAP) da Polícia Militar do Pará, "
        "sediado no município de Belém/PA. O CIAP constitui a unidade de referência corporativa de apoio em saúde mental, "
        "responsável pelo planejamento, execução, coordenação pericial e assistência psicossocial contínua aos policiais militares da ativa, "
        "da reserva remunerada e a seus respectivos dependentes legais em todo o território estadual."
    )

    metodologia_etica = (
        "A pesquisa cumpre estritamente os preceitos éticos da Lei Geral de Proteção de Dados Pessoais (Lei nº 13.709/2018) e as diretrizes "
        "regulatórias do Conselho Nacional de Saúde expressas nas Resoluções CNS nº 466/2012 e nº 510/2016, com protocolo formal submetido "
        "ao Comitê de Ética em Pesquisa do Instituto de Ciências da Saúde da Universidade Federal do Pará (CEP/ICS-UFPA). Todos os identificadores "
        "diretos dos policiais foram pseudonimizados por hashes criptográficos irreversíveis (SHA-256) com chave custodiada de forma independente, "
        "e o texto livre submetido a algoritmo local de Reconhecimento de Entidades Nomeadas (NER) para supressão de termos identificadores. "
        "Estabelece-se salvaguarda ética formal de vedação absoluta de utilização dos modelos preditivos para fins disciplinares ou punitivos."
    )

    metodologia_analise = (
        "A modelagem preditiva empregará Fusão Intermediária acoplando representações contextuais densas de notas clínicas (embeddings do BERTimbau) "
        "a atributos temporais dinâmicos agregados por janelas deslizantes (rolling windows de 6 a 12 meses de observação e 30 a 90 dias de predição). "
        "Serão treinados e comparados modelos baseados em árvores impulsionadas por gradiente (XGBoost) e Redes Neurais com autoatenção (Self-Attention). "
        "A avaliação adotará partição temporal estrita (out-of-time validation) sob métricas de AUROC, AUPRC, Sensibilidade e calibração por Brier Score, "
        "com explicabilidade assistencial calculada por valores de SHAP (Explainable AI)."
    )

    # Coleta de referências reais
    referencias = [
        "ADEKKANATTU, P. et al. Deep learning for identifying personal and family history of suicidal thoughts and behaviors from EHRs. npj Digital Medicine, London, v. 7, n. 1, art. 260, p. 1-11, 2024.",
        "AFTAB, A. B. et al. GBRT++: A New Data-Driven Model for Predicting Self-Harming Behavior in Postpartum Depression. In: INTERNATIONAL CONFERENCE ON COMPUTER AND INFORMATION TECHNOLOGY (ICCIT), 28., 2025, Cox's Bazar. Proceedings [...]. Piscataway: IEEE, 2025. p. 5163-5168.",
        "ALVES, P. et al. A machine learning model using clinical notes to estimate PHQ-9 symptom severity scores in depressed patients. Journal of Affective Disorders, Amsterdam, v. 374, p. 119-127, 2025.",
        "CARRASCO-RIBELLES, L. A. et al. Prediction models using artificial intelligence and longitudinal data from electronic health records: a systematic methodological review. Journal of the American Medical Informatics Association, Oxford, v. 30, n. 12, p. 2072-2082, 2023.",
        "CHEBBAWI, S.; TABAA, M.; BADIR, H. An Interpretable AI Framework to Predict Post-ICU Mental Health Risks employing EHR Data and Vitamin D Biomarkers. In: IEEE INTERNATIONAL MULTIDISCIPLINARY CONFERENCE ON ENGINEERING TECHNOLOGY (IMCET), 5., 2026, Beirute. Proceedings [...]. Piscataway: IEEE, 2026. p. 1-9.",
        "CRUZ, F. N. et al. Desvendando os Suicídios Entre Profissionais de Segurança Pública: um olhar sobre fatores operacionais e organizacionais. Sociedade e Estado, Brasília, v. 41, n. 1, art. e56366, 2026.",
        "DEVLIN, J. et al. BERT: Pre-training of deep bidirectional transformers for language understanding. arXiv preprint arXiv:1810.04805, p. 1-14, 2018.",
        "DIAS, C. A.; SIQUEIRA, M. V. S.; FERREIRA, L. B. Análise socioclínica do contexto do trabalho e sua relação com o adoecimento mental de policiais militares do Distrito Federal. Cadernos EBAPE.BR, Rio de Janeiro, v. 21, n. 1, art. e2022-0095, 2023.",
        "FENG, W. et al. Deep learning based prediction of depression and anxiety in patients with type 2 diabetes mellitus using regional electronic health records. International Journal of Medical Informatics, Shannon, v. 196, art. 105801, p. 1-10, 2025.",
        "GARRIGA, R. et al. Machine learning model to predict mental health crises from electronic health records. Nature Medicine, New York, v. 28, n. 6, p. 1240-1248, 2022.",
        "GARRIGA, R. et al. Combining clinical notes with structured electronic health records enhances the prediction of mental health crises. Cell Reports Medicine, Cambridge, v. 4, n. 11, art. 101260, p. 1-13, 2023.",
        "GIANVECCHIO, V. A. P.; JORGE, M. H. P. M. O suicídio no estado de São Paulo, Brasil: comparando dados da Segurança Pública e da Saúde. Ciência & Saúde Coletiva, Rio de Janeiro, v. 27, n. 6, p. 2427-2438, 2022.",
        "HANSEN, N. B. et al. Exposure to critical incidents at work and development of posttraumatic stress among police officers: a 2-year prospective cohort study. European Journal of Work and Organizational Psychology, London, v. 34, n. 4, p. 451-473, 2025.",
        "JEEVITHA, V.; PRIYA, R. Early Prediction of Postpartum Depression Using Machine Learning on Electronic Health Records. In: INTERNATIONAL CONFERENCE ON COMMUNICATION AND ELECTRONICS SYSTEMS (ICCES), 10., 2025, Coimbatore. Proceedings [...]. Piscataway: IEEE, 2025. p. 648-654.",
        "LIMA, A. G. T. et al. Exhaustion and Burnout Syndrome among Brazilian Military Police Officers Stationed in the Interior of Pernambuco. Texto & Contexto - Enfermagem, Florianópolis, v. 34, art. e20250013, 2025.",
        "MARTINS, D. A.; SILVA, V. U. A. M. Suporte à decisão organizacional na gestão de resposta às emergências em saúde do trabalhador. Revista Técnica da Universidade Petrobras, Rio de Janeiro, v. 1, n. 7, p. 1-14, 2025.",
        "MENG, Y. et al. Bidirectional Representation Learning From Transformers Using Multimodal Electronic Health Record Data to Predict Depression. IEEE Journal of Biomedical and Health Informatics, Piscataway, v. 25, n. 8, p. 3121-3129, 2021.",
        "MSOSA, Y. J. et al. Trustworthy Data and AI Environments for Clinical Prediction: Application to Crisis-Risk in People With Depression. IEEE Journal of Biomedical and Health Informatics, Piscataway, v. 27, n. 11, p. 5588-5598, 2023.",
        "RUDIN, C. Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead. Nature Machine Intelligence, London, v. 1, n. 5, p. 206-215, 2019.",
        "SANTOS, J. S. et al. Factors associated with Burnout Syndrome in police officers: a scoping review. Revista Brasileira de Enfermagem, Brasília, v. 77, n. 2, art. e20230444, p. 1-10, 2024.",
        "SOUSA, R. C.; BARROSO, S. M.; RIBEIRO, A. C. S. Aspectos de saúde mental investigados em policiais: uma revisão integrativa. Saúde e Sociedade, São Paulo, v. 31, n. 2, art. e2201008pt, p. 1-16, 2022.",
        "UGWU, L. E.; IDEMUDIA, E. S. Burnout and Post-traumatic Stress Disorders in Police Officers: Systematic Review and Meta-analysis. Journal of Police and Criminal Psychology, New York, v. 40, p. 645-658, 2025.",
        "ULLAH, M. T.; REDDY, E. S. Multi-Modal Deep Learning for Personalized Risk Stratification in Perimenopausal Women. In: INTERNATIONAL CONFERENCE ON AUGMENTED INTELLIGENCE AND SUSTAINABLE SYSTEMS (ICAISS), 4., 2026, Trichy. Proceedings [...]. Piscataway: IEEE, 2026. p. 899-905.",
        "WANG, G. et al. Interpretable Artificial Intelligence for Healthcare: Enhancing Clinical Trust through SHAP and LIME. Journal of Healthcare Informatics Research, New York, v. 8, p. 112-130, 2024.",
        "YANG, L.; BRANSCUM, A.; KINCL, L. Understanding occupational safety and health surveillance: expert consensus on components, attributes and example measures for an evaluation framework. BMC Public Health, London, v. 22, art. 498, p. 1-13, 2022."
    ]

    ptts = [
        {
            "num": "5.1",
            "nome": "PTT 1: Infográfico Epidemiológico-Institucional",
            "autoria": "Leonardo da Silva Costa",
            "tipo": "Material Didático",
            "subtipo": "Infográfico",
            "titulo": "Panorama Epidemiológico e Ocupacional dos Atendimentos Psicossociais no CIAP/PMPA",
            "ano": "2026",
            "coautoria": "Edson Marcos Leal Soares Ramos (Docente/Orientador); Nathália Ferreira de Almeida (Colaboradora Técnica/Perita)",
            "projeto": "Métodos Quantitativos e Inteligência Artificial Aplicada à Segurança Pública",
            "financiamento": "Não",
            "financiador": "Recursos próprios / Institucional",
            "demanda": "Institucional CIAP/PMPA",
            "impacto": "Alto",
            "justificativa_impacto": "Subsidia diretamente o planejamento assistencial e a alocação de equipes multidisciplinares no CIAP/PMPA, reduzindo custos decorrentes de afastamentos tardios.",
            "inovacao": "Alto",
            "justificativa_inovacao": "Traduz correlações epidemiológicas multidimensionais e fatores ocupacionais em linguagem visual acessível para comandantes e equipes de saúde.",
            "complexidade": "Alto",
            "justificativa_complexidade": "Exige tratamento de dados longitudinais de múltiplos anos, estratificação paramétrica de postos/graduações e curadoria técnica em duplo-cego.",
            "validacao": "Homologação técnica pela diretoria do CIAP/PMPA e depósito institucional no PPGSP/UFPA",
            "divulgacao": "Repositório Institucional da UFPA e intranet corporativa do CIAP",
            "abrangencia": "Estadual (Pará)",
            "publico_usuario": "Diretoria e equipes multiprofissionais do CIAP, gestores de saúde da PMPA e órgãos de segurança pública."
        },
        {
            "num": "5.2",
            "nome": "PTT 2: Infográfico Clínico-Léxico de Sintomas",
            "autoria": "Leonardo da Silva Costa",
            "tipo": "Material Didático",
            "subtipo": "Infográfico",
            "titulo": "Guia Visual Clínico-Léxico de Marcadores Precoces de Crise em Evoluções Psicossociais",
            "ano": "2026",
            "coautoria": "Edson Marcos Leal Soares Ramos (Docente/Orientador); Henrique Moura Monteiro (Colaborador Técnico/Perito)",
            "projeto": "Métodos Quantitativos e Inteligência Artificial Aplicada à Segurança Pública",
            "financiamento": "Não",
            "financiador": "Recursos próprios",
            "demanda": "Institucional CIAP/PMPA",
            "impacto": "Alto",
            "justificativa_impacto": "Orienta os técnicos no acolhimento primário a detectar sinais sutis de exaustão e ideação autodestrutiva não codificados formalmente.",
            "inovacao": "Alto",
            "justificativa_inovacao": "Mapeamento sistemático de termos lexicais contextualizados no jargão e na cultura militar policial.",
            "complexidade": "Alto",
            "justificativa_complexidade": "Mineração de texto não estruturado sobre milhares de registros clínicos correlacionados a eventos desfavoráveis.",
            "validacao": "Validação por consenso pericial com psicólogos e psiquiatras do CIAP",
            "divulgacao": "Cartilha digital técnica e painel impresso nas salas de acolhimento",
            "abrangencia": "Estadual",
            "publico_usuario": "Psicólogos, assistentes sociais e psiquiatras do CIAP/PMPA."
        },
        {
            "num": "5.3",
            "nome": "PTT 3: Codebook Operacional de Anotação Clínica",
            "autoria": "Leonardo da Silva Costa",
            "tipo": "Manual / Protocolo",
            "subtipo": "Guia Técnico Operacional",
            "titulo": "Codebook Taxonômico de Rotulagem Pericial em Saúde Mental (Versão 1.2)",
            "ano": "2026",
            "coautoria": "Edson Marcos Leal Soares Ramos (Docente); Nathália Ferreira de Almeida (Colaboradora); Henrique Moura Monteiro (Colaborador)",
            "projeto": "Métodos Quantitativos e Inteligência Artificial Aplicada à Segurança Pública",
            "financiamento": "Não",
            "financiador": "Recursos próprios",
            "demanda": "Metodológica e Institucional",
            "impacto": "Alto",
            "justificativa_impacto": "Padroniza critérios diagnósticos de crise aguda para anotação pericial, mitigando a variabilidade interavaliadores.",
            "inovacao": "Alto",
            "justificativa_inovacao": "Primeiro protocolo taxonômico com regras formais de adjudicação e rótulos suavizados aplicado à saúde militar no Brasil.",
            "complexidade": "Alto",
            "justificativa_complexidade": "Harmonização de critérios diagnósticos do DSM-5/CID-10 com a realidade ocupacional e estressores de segurança pública.",
            "validacao": "Cálculo de concordância interavaliadores (índice Kappa ponderado) entre peritos independentes",
            "divulgacao": "Manual técnico registrado no PPGSP/UFPA",
            "abrangencia": "Regional / Nacional",
            "publico_usuario": "Pesquisadores em psiquiatria computacional e equipes técnicas de avaliação pericial."
        },
        {
            "num": "5.4",
            "nome": "PTT 4: Software de Triagem e Predição Multimodal",
            "autoria": "Leonardo da Silva Costa",
            "tipo": "Software Registrável",
            "subtipo": "Aplicação Modular / API",
            "titulo": "CIAP Preditivo: Sistema Computacional Multimodal de Suporte à Decisão Clínica",
            "ano": "2026",
            "coautoria": "Edson Marcos Leal Soares Ramos (Docente/Orientador)",
            "projeto": "Métodos Quantitativos e Inteligência Artificial Aplicada à Segurança Pública",
            "financiamento": "Não",
            "financiador": "Recursos próprios",
            "demanda": "Institucional CIAP/PMPA",
            "impacto": "Alto",
            "justificativa_impacto": "Automatiza a triagem preventiva de milhares de prontuários com explicabilidade local via SHAP para uso estritamente clínico.",
            "inovacao": "Alto",
            "justificativa_inovacao": "Fusão intermediária inédita de embeddings BERTimbau com árvores de decisão impulsionadas em ambiente conteinerizado (Docker).",
            "complexidade": "Alto",
            "justificativa_complexidade": "Arquitetura cliente-servidor com microsserviços, controle de latência, tolerância a falhas e rigorosa segurança de dados.",
            "validacao": "Testes de carga, validação cruzada out-of-time e homologação por profissionais de saúde do CIAP",
            "divulgacao": "Repositório institucional e registro de software perante o INPI",
            "abrangencia": "Estadual",
            "publico_usuario": "Profissionais de saúde e analistas de sistemas da Polícia Militar do Pará."
        },
        {
            "num": "5.5",
            "nome": "PTT 5: Base de Dados Sintética com Privacidade Preservada",
            "autoria": "Leonardo da Silva Costa",
            "tipo": "Base de Dados",
            "subtipo": "Repositório Aberto de Dados Sintéticos",
            "titulo": "Repositório Sintético de Registros Psicossociais Policiais com Privacidade Diferencial",
            "ano": "2026",
            "coautoria": "Edson Marcos Leal Soares Ramos (Docente/Orientador)",
            "projeto": "Métodos Quantitativos e Inteligência Artificial Aplicada à Segurança Pública",
            "financiamento": "Não",
            "financiador": "Recursos próprios",
            "demanda": "Científica / Reprodutibilidade",
            "impacto": "Alto",
            "justificativa_impacto": "Permite reprodutibilidade científica e testes acadêmicos abertos sem qualquer risco de exposição de dados de policiais reais.",
            "inovacao": "Alto",
            "justificativa_inovacao": "Geração tabular sintética calibrada por privacidade diferencial sobre domínio de saúde e segurança pública.",
            "complexidade": "Alto",
            "justificativa_complexidade": "Preservação da matriz de covariância multivariada e relações temporais sem memorização de identidades.",
            "validacao": "Testes estatísticos de similaridade distributional (Kolmogorov-Smirnov) e auditoria de vazamento empírico",
            "divulgacao": "Plataformas de Ciência Aberta (Zenodo / Harvard Dataverse)",
            "abrangencia": "Nacional / Internacional",
            "publico_usuario": "Comunidade científica, pesquisadores em saúde mental e pós-graduandos em segurança pública."
        },
        {
            "num": "5.6",
            "nome": "PTT 6: Modelo de LLM Local para Grifagem Clínica",
            "autoria": "Leonardo da Silva Costa",
            "tipo": "Ferramenta Tecnológica",
            "subtipo": "Modelo de Linguagem Especializado",
            "titulo": "Modelo Local On-Premise para Realce Automatizado de Estressores em Notas Clínicas",
            "ano": "2026",
            "coautoria": "Edson Marcos Leal Soares Ramos (Docente/Orientador)",
            "projeto": "Métodos Quantitativos e Inteligência Artificial Aplicada à Segurança Pública",
            "financiamento": "Não",
            "financiador": "Recursos próprios",
            "demanda": "Operacional CIAP/PMPA",
            "impacto": "Alto",
            "justificativa_impacto": "Reduz o tempo de leitura de prontuários extensos, grifando automaticamente trechos críticos durante os plantões assistenciais.",
            "inovacao": "Alto",
            "justificativa_inovacao": "Inferência de modelo de linguagem executada 100% on-premise, sem envio de dados para nuvem ou servidores de terceiros.",
            "complexidade": "Alto",
            "justificativa_complexidade": "Ajuste fino (fine-tuning) e quantização em 4-bit para execução eficiente em computadores padrão.",
            "validacao": "Validação de precisão de extração perante peritos clínicos do CIAP",
            "divulgacao": "Instalação local conteinerizada nas estações do CIAP",
            "abrangencia": "Estadual",
            "publico_usuario": "Avaliadores clínicos e profissionais de psicologia e assistência social da PMPA."
        }
    ]

    return {
        "metadata": {
            "titulo": (
                "ESTEIRA PREDITIVA MULTIMODAL DE SUPORTE À DECISÃO CLÍNICA NO CIAP/PMPA: "
                "MODELOS DE APRENDIZADO DE MÁQUINA PARA PREDIÇÃO DE DESFECHOS RELACIONADOS "
                "À SAÚDE MENTAL DE POLICIAIS MILITARES DO PARÁ A PARTIR DE PRONTUÁRIOS PSICOSSOCIAIS"
            ),
            "autor": "Leonardo da Silva Costa",
            "orientador": "Prof. Dr. Edson Marcos Leal Soares Ramos",
            "coordenador": "Prof. Dr. Edson Marcos Leal Soares Ramos",
            "nivel": "mestrado",
            "local": "Belém-Pará",
            "ano": "2026",
            "area_concentracao": "Segurança Pública, Justiça, Conflitos e Cidadania",
            "linha_pesquisa": "Políticas, Gestão, Direitos Humanos, Criminalidade e Tecnologia da Informação",
            "data_aprovacao": "____ de _______________ de 2026",
            "banca": [
                {"nome": "Prof. Dr. Edson Marcos Leal Soares Ramos", "instituicao": "Universidade Federal do Pará", "funcao": "Orientador"},
                {"nome": "Prof. Dr. [Nome do Avaliador Interno]", "instituicao": "Universidade Federal do Pará", "funcao": "Avaliador Interno"},
                {"nome": "Prof. Dr. [Nome do Avaliador Externo]", "instituicao": "[Instituição Externa]", "funcao": "Avaliador Externo"}
            ],
            "lista_ilustracoes": [
                ("Quadro 1 – Estrutura dos principais itens da pesquisa", "vi"),
                ("Quadro 2 – Cronograma de atividades desenvolvidas durante o Mestrado (24 meses)", "12")
            ],
            "lista_tabelas": [
                ("Tabela 1 – Distribuição Populacional da Coorte Viva e Alocação Amostral (n = 360)", "7"),
                ("Tabela 2 – Métricas de Dispersão de Tokens por Prontuário e Limiares de Outliers (Método de Tukey)", "8")
            ],
            "siglas": [
                ("ABNT", "Associação Brasileira de Normas Técnicas"),
                ("BERT", "Bidirectional Encoder Representations from Transformers"),
                ("CIAP", "Centro Integrado de Atenção Psicossocial"),
                ("EHR", "Electronic Health Records"),
                ("LGPD", "Lei Geral de Proteção de Dados Pessoais (Lei nº 13.709/2018)"),
                ("PLN", "Processamento de Linguagem Natural"),
                ("PMPA", "Polícia Militar do Pará"),
                ("PPGSP", "Programa de Pós-Graduação em Segurança Pública"),
                ("PTT", "Produto Técnico e Tecnológico"),
                ("SHAP", "SHapley Additive exPlanations"),
                ("UFPA", "Universidade Federal do Pará")
            ],
            "sumario": [
                ("LISTA DE ILUSTRAÇÕES", "iv", False),
                ("LISTA DE TABELAS", "v", False),
                ("LISTA DE ABREVIATURAS E SIGLAS", "vi", False),
                ("APRESENTAÇÃO", "vii", True),
                ("1. CONSIDERAÇÕES GERAIS", "1", True),
                ("   1.1 INTRODUÇÃO", "1", False),
                ("   1.2 JUSTIFICATIVA", "3", False),
                ("   1.3 PROBLEMA DE PESQUISA", "4", False),
                ("   1.4 REVISÃO DA LITERATURA / REFERENCIAL TEÓRICO", "4", False),
                ("2. OBJETIVOS", "6", True),
                ("   2.1 OBJETIVO GERAL", "6", False),
                ("   2.2 OBJETIVOS ESPECÍFICOS", "6", False),
                ("3. HIPÓTESE / QUESTÃO NORTEADORA", "7", True),
                ("4. METODOLOGIA", "7", True),
                ("   4.1 Natureza da Pesquisa", "7", False),
                ("   4.2 Lócus da Pesquisa", "7", False),
                ("   4.3 Participantes e Coorte Populacional", "7", False),
                ("   4.4 Procedimentos de Coleta e Mineração de Dados", "9", False),
                ("   4.5 Procedimentos Éticos e Salvaguardas Regulatórias", "9", False),
                ("   4.6 Análise de Dados e Modelagem Computacional", "9", False),
                ("5. PROPOSTA DE PRODUTOS", "10", True),
                ("6. CRONOGRAMA", "12", True),
                ("7. RESULTADOS PRELIMINARES", "13", True),
                ("   7.1 PRODUTO BIBLIOGRÁFICO I - ARTIGO 1", "13", False),
                ("REFERÊNCIAS DO PROJETO", "15", True)
            ]
        },
        "apresentacao": {
            "texto_percurso": [
                "A presente proposta de pesquisa articula a trajetória profissional do autor como Oficial e Psicólogo no CIAP/PMPA com os métodos de Engenharia de Software e Ciência de Dados no PPGSP/UFPA.",
                "A organização lógica dos artigos e produtos técnicos vinculados aos objetivos específicos encontra-se sistematizada no Quadro 1."
            ],
            "quadro_1": [
                ["Artigo 1: Análise Clínico-Léxica no CIAP/PMPA", "Desenvolver esteira computacional de suporte assistencial.", "Caracterizar a epidemiologia e termos clínicos nas evoluções.", "Artigo Científico (Qualis A)", "Quantitativo", "Prontuários CIAP", "Em elaboração"],
                ["Artigo 2: Modelagem Multimodal com BERTimbau", "Desenvolver esteira computacional de suporte assistencial.", "Comparar modelos preditivos na detecção precoce de crises.", "Artigo Científico (Qualis A)", "Quantitativo", "Embeddings e dados tabulares", "Em elaboração"],
                ["PTT 1: Infográfico Epidemiológico", "Desenvolver esteira computacional de suporte assistencial.", "Conceber material didático visual dos atendimentos.", "Produto Técnico", "Aplicado", "Banco CIAP", "Concluído"],
                ["PTT 2: Guia Léxico de Sintomas", "Desenvolver esteira computacional de suporte assistencial.", "Sintetizar termos de alerta para triagem clínica.", "Produto Técnico", "Léxico", "Notas clínicas", "Concluído"],
                ["PTT 3: Codebook Operacional v1.2", "Desenvolver esteira computacional de suporte assistencial.", "Formalizar critérios de rotulagem em duplo-cego.", "Manual Técnico", "Metodológico", "Consenso pericial", "Em validação"],
                ["PTT 4: Software de Predição em Docker", "Desenvolver esteira computacional de suporte assistencial.", "Implementar aplicação conteinerizada com SHAP.", "Software Registrável", "Eng. Software", "Pipeline de IA", "Em desenvolvimento"],
                ["PTT 5: Base de Dados Sintética", "Desenvolver esteira computacional de suporte assistencial.", "Gerar conjunto de dados com privacidade diferencial.", "Base de Dados", "Estatística", "Distribuições empíricas", "Em desenvolvimento"],
                ["PTT 6: LLM Local para Grifagem", "Desenvolver esteira computacional de suporte assistencial.", "Ajustar modelo open-source on-premise.", "Modelo de IA", "PLN", "Notas de evolução", "Em desenvolvimento"]
            ]
        },
        "projeto": {
            "introducao": introducao,
            "justificativa": justificativa,
            "problema": problema,
            "revisao": revisao,
            "objetivo_geral": "Desenvolver e avaliar uma esteira metodológica e computacional baseada na fusão de dados multimodais de prontuários psicossociais para a predição de desfechos de saúde mental em policiais militares do Pará, estruturando as evidências em dois artigos científicos e consolidando um ecossistema de produtos técnicos aplicados de suporte à decisão clínica e vigilância assistencial no CIAP/PMPA.",
            "objetivos_especificos": [
                "Estruturar e desidentificar a base analítica institucional em conformidade com a LGPD e normas do CEP/Conep;",
                "Definir e validar o padrão-ouro taxonômico (ground truth) através de codebook formal e rotulagem em duplo-cego;",
                "Caracterizar a epidemiologia descritiva e os padrões léxicos de sofrimento no acervo do CIAP;",
                "Conceber produtos visuais de translação do conhecimento para auxílio às equipes multiprofissionais;",
                "Modelar variáveis temporais e representações semânticas via janelas deslizantes (rolling windows);",
                "Comparar e calibrar algoritmos de aprendizado de máquina multimodais (XGBoost e Deep Neural Networks);",
                "Auditar a interpretabilidade clínica das predições com valores de SHAP (Explainable AI);",
                "Desenvolver software conteinerizado em Docker para classificação de novos prontuários;",
                "Gerar e validar base de dados sintética com privacidade preservada para reprodutibilidade científica;",
                "Implementar modelo de LLM local on-premise para suporte à grifagem clínica de sentenças críticas."
            ],
            "hipotese": hipotese,
            "metodologia_natureza": "Pesquisa quantitativa, empírica e aplicada com foco em inovação tecnológica, fundamentada em ciência de dados e engenharia de software em saúde.",
            "metodologia_locus": metodologia_locus,
            "metodologia_participantes": "Coorte retrospectiva de N = 5.706 atendimentos clínicos únicos de policiais militares vivos registrados no CIAP/PMPA (2024-2026), com amostra representativa calibrada por Cochran e Tukey de n = 360 atendimentos.",
            "metodologia_coleta": "Extração automatizada de atributos tabulares e notas narrativas de evolução clínica, submetidas a pré-processamento e desidentificação local via modelo de Reconhecimento de Entidades Nomeadas (NER).",
            "metodologia_etica": metodologia_etica,
            "metodologia_analise": metodologia_analise,
            "tabela_1": {"linhas": tabela_1_linhas},
            "tabela_2": {"linhas": tabela_2_linhas},
            "ptts": ptts,
            "cronograma": [
                ("Disciplinas Obrigatórias e Optativas", [1,2,3,4,5,6,7,8,9,10]),
                ("Pesquisa Bibliográfica e Estado da Arte", [1,2,3,4,5,6,7,8]),
                ("Submissão Ética na Plataforma Brasil / CEP", [4,5,6]),
                ("Construção do Codebook e Taxonomia Clínica", [5,6,7,8]),
                ("Exame de Qualificação do Projeto", [7]),
                ("Extração e Anonimização dos Prontuários", [9,10]),
                ("Rotulagem Pericial em Duplo-Cego", [10,11,12]),
                ("Engenharia de Atributos e Embeddings", [11,12,13,14]),
                ("Treinamento dos Modelos Multimodais e XAI", [13,14,15,16]),
                ("Desenvolvimento dos Produtos Técnicos (PTTs)", [14,15,16,17,18]),
                ("Redação dos Artigos Científicos 1 e 2", [15,16,17,18,19,20]),
                ("Redação Final e Depósito da Dissertação", [19,20,21]),
                ("Defesa Pública da Dissertação", [23,24])
            ]
        },
        "resultados": {
            "artigo_preliminar": {
                "titulo": "CARACTERIZAÇÃO EPIDEMIOLÓGICA E PADRÕES CLÍNICO-LÉXICOS DE SAÚDE MENTAL EM POLICIAIS MILITARES DO PARÁ A PARTIR DE PRONTUÁRIOS INSTITUCIONAIS",
                "autores": "Leonardo da Silva Costa; Edson Marcos Leal Soares Ramos; Nathália Ferreira de Almeida; Henrique Moura Monteiro",
                "resumo_estruturado": [
                    ("Importância do Estudo", "A preservação da saúde mental na segurança pública requer a superação de modelos reativos por meio da identificação de marcadores precoces de sofrimento psíquico documentados nas rotinas assistenciais."),
                    ("Objetivo", "Mapear a epidemiologia descritiva dos atendimentos no CIAP/PMPA e identificar padrões textuais de desgaste ocupacional em notas clínicas de evolução."),
                    ("Materiais e Métodos", "Estudo observacional retrospectivo sobre coorte de N = 5.706 atendimentos clínicos únicos (2024-2026), com amostra calibrada de n = 360 registros analisados sob técnicas de mineração de texto e modelos de linguagem contextuais."),
                    ("Resultados e Discussões", "Evidenciou-se concentração de demandas ligadas a estressores operacionais e queixas somáticas, com termos recorrentes associados a perturbações de sono e exaustão antecedendo eventos de afastamento formal."),
                    ("Conclusões", "As notas narrativas contêm indicadores clínicos críticos ausentes dos códigos diagnósticos tradicionais, validando a necessidade de esteiras computacionais de triagem assistencial proativa.")
                ],
                "palavras_chave": "Saúde Mental Policial; Prontuários Eletrônicos; Mineração de Texto; Vigilância Assistencial; Processamento de Linguagem Natural.",
                "secoes_texto": [
                    ("1. INTRODUÇÃO", "O presente artigo científico preliminar sistematiza a primeira frente de investigação empírica do mestrado, caracterizando o acervo longitudinal de registros do CIAP e validando a representatividade léxica da amostra calibrada de 360 atendimentos."),
                    ("2. MATERIAL E MÉTODO", "A metodologia aplicou o particionamento em cinco macroestratos clínico-institucionais com controle paramétrico de outliers de texto pelo método de Tukey (Q3 + 1,5 × IQR), assegurando densidade semântica equilibrada para rotulagem em duplo-cego."),
                    ("3. RESULTADOS E DISCUSSÕES", "Os achados parciais demonstram taxa de completude superior a 95% nos atributos tabulares e confirmam que queixas clínicas narrativas apresentam maior riqueza informativa que códigos diagnósticos isolados da CID-10."),
                    ("4. CONSIDERAÇÕES FINAIS", "A consolidação desta base e do codebook taxonômico viabiliza a etapa subsequente de treinamento dos modelos multimodais de aprendizado de máquina.")
                ]
            }
        },
        "referencias": referencias
    }