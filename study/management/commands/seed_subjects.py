
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Sum

from study.models import Subject, Unit, Topic


SOURCE = (
    "https://portal.tu.edu.np/downloads/"
    "syllabus34136_2023_05_10_06_50_22.pdf"
)

VERSION = "TU IoST B.Sc. 4-year Revised Course of Study 2073"


# Format:
# (unit_code, unit_title, lecture_hours, [official syllabus topics])
#
# Practical papers are intentionally not included.

COURSES = [
    {
        "code": "CHE301",
        "title": "General Chemistry I",
        "category": "core",
        "full_marks": 100,
        "pass_marks": "35",
        "hours": 150,
        "units": [
            (
                "Group A",
                "Inorganic Chemistry",
                50,
                [
                    "Hydrogen: isotopes of hydrogen; general study of hydrides and their classification.",
                    "Noble gases and their compounds: preparation, properties and structure of xenon fluorides and oxo-compounds; valence bond treatment; VSEPR treatment; molecular orbital treatment for XeF2.",
                    "Boron compounds: preparation, properties, bonding and structure of boric acid, borates, boron nitride, borazines, boron hydrides and metal borohydrides.",
                    "Silicon compounds: preparation, properties, bonding and structure of silicates, silicones, silanes and siloxanes.",
                    "Interhalogen compounds, pseudohalogens and pseudohalides: preparation, properties, bonding and structure.",
                    "Electronegativity: review; electronegativity equalization; recent advances in electronegativity theory; variation of electronegativity; choice of electronegativity system; group electronegativity.",
                    "Electron affinity and ionization energy: anomalous ionization energies and electron affinities; alternation of electronegativities in heavier elements.",
                    "Chemical fertilizers: nitrogen fixation and synthetic fertilizers; importance of chemical fertilizers; nitrogen cycle; main ingredients of plant fertilizers; major and minor nutrients.",
                    "Manufacture of fertilizers: Haber-Bosch process for NH3; nitrogenase; model systems for systems absorbing dinitrogen and production of NH3; cyanamide process; manufacture of urea; phosphate fertilizers; environmental impact of chemical fertilizers.",
                    "Environmental pollution: elementary study of air, water and soil pollution.",
                    "Air pollution: sources; emissions; anthropogenic emissions of gases and particulate matter; acid rain; smog; depletion of ozone layer.",
                    "Water pollution: dissolved oxygen; total alkalinity; biochemical oxygen demand; chemical oxygen demand; eutrophication; classification of water pollutants; control of water pollution.",
                    "Soil pollution: introduction; sources; acid rain; repeated use of same fertilizers; inadequate drainage in agricultural fields; application of pesticides and radioactive wastes.",
                ],
            ),
            (
                "Group B",
                "Organic Chemistry",
                50,
                [
                    "Organic reactions and mechanisms: types of mechanisms and reactions; thermodynamic and kinetic requirements for reactions.",
                    "Organic reaction mechanisms: Baldwin's rules of ring closure; kinetic and thermodynamic control; Hammond postulate; microscopic reversibility.",
                    "Methods of determining reaction mechanisms: identification of products; determination of intermediates; study of catalysis; isotope labelling; stereochemical evidence; first- and second-order rate expressions; isotope effect.",
                    "Reactive intermediates: stability, structure, generation and fate of carbocations, carbanions, carbenes, nitrenes and benzynes.",
                    "Nonclassical carbonium ions and neighbouring group participation by pi and sigma bonds.",
                    "Free radicals: history and characteristics; formation, propagation, termination, reactivity and stereochemistry.",
                    "Free radical reactions: fragmentation, substitution, addition, oxidation and reduction; detection of free radicals.",
                    "Spectroscopy: introduction to electromagnetic spectrum; infrared spectrum; ultraviolet spectrum; nuclear magnetic resonance spectroscopy.",
                    "Proton NMR: number of signals; equivalent and non-equivalent protons; chemical shift; peak area; proton coupling; spin-spin coupling; coupling constant.",
                    "Carbon-13 NMR: carbon-13 chemical shift; proton and carbon-13 NMR spectra of simple hydrocarbons, alcohols, aldehydes, ketones, carboxylic acids, amines, phenols, ethers and aromatic compounds.",
                    "Mass spectrum and its application in structure determination.",
                    "Heterocyclic systems: structure and sources of pyrrole, furan and thiophene; electrophilic substitution, reactivity and orientation.",
                    "Saturated five-membered heterocycles; structure and sources of pyridine compounds.",
                    "Pyridine: reactions; electrophilic and nucleophilic substitution; basicity; reduction.",
                ],
            ),
            (
                "Group C",
                "Physical Chemistry",
                50,
                [
                    "Electrolytic conductance: failure of Arrhenius theory for strong electrolytes; Debye-Huckel theory of interionic attraction for electrolytic conduction (elementary treatment).",
                    "Electrolyte activity: activity and activity coefficients; ionic strength; Debye-Huckel limiting law (elementary treatment).",
                    "Electrochemical cells: reversible and irreversible cells; types of reversible electrodes; thermodynamics of reversible electrodes and cells.",
                    "Thermodynamic quantities from cell EMF: delta G, delta H, delta S and equilibrium constant.",
                    "Chemical cells with and without transference; concentration cells with and without transference; liquid junction potential.",
                    "Applications of EMF measurement: determination of activities and activity coefficients; formal and standard electrode potentials; solubility products.",
                    "Spectroscopy: electromagnetic radiation; atomic and molecular spectra; origin of molecular spectra; classification of molecular spectra.",
                    "Rotational spectroscopy: microwave spectrum; rigid and non-rigid rotors; energy levels of rigid rotor; selection rules; applications.",
                    "Vibrational spectroscopy: infrared spectrum; simple harmonic oscillator; energy levels; selection rules; pure vibrational spectrum; anharmonic motion; vibrational frequencies of functional groups.",
                    "Raman spectroscopy: polarizability; pure rotational and pure vibrational Raman spectra of diatomic molecules; selection rules.",
                    "Electronic spectroscopy: introduction; Franck-Condon principle; selection rules; applications.",
                    "Polymer chemistry: introduction and classification of polymers and copolymers; crystalline, amorphous, thermoplastic and thermosetting properties.",
                    "Polymerization: addition and condensation polymerization; degree of polymerization; average molecular weight; determination by osmometry, light scattering and viscosity measurement; solutions of macromolecules.",
                    "Thermodynamics: entropy; entropy change in isolated systems; dependence on temperature, volume and pressure; entropy change in ideal gases; entropy of mixing; entropy changes in physical and chemical transformations.",
                    "Third law of thermodynamics and its significance; free energy change; Gibbs free energy change; Gibbs-Helmholtz equation; variation with temperature and pressure.",
                    "Thermodynamic equilibrium: calculation of free energy change; reaction isotherm; thermodynamic criterion of equilibrium; Clapeyron equation; Clausius-Clapeyron equation.",
                    "Equilibrium constants: thermodynamic equilibrium constant; Kp and Kc for gaseous reactions; variation with temperature; quantitative thermodynamic treatment of Le-Chatelier's principle; related numerical problems.",
                ],
            ),
        ],
    },

    {
        "code": "BOT301",
        "title": "Plant Biochemistry and Biotechnology",
        "category": "core",
        "full_marks": 100,
        "pass_marks": "35",
        "hours": 150,
        "units": [
            (
                "Unit A",
                "Plant Biochemistry",
                75,
                [
                    "Introduction: plant biochemistry as a science.",
                    "Relationship between plant biochemistry and plant sciences, including genetics, cell biology, molecular biology, plant physiology and other branches of biosciences.",
                    "Water: molecular structure and properties; water as a solvent; ionization of water; pH scale; buffers.",
                    "Functional groups found in biomolecules: general concept.",
                    "Carbohydrates: definition and classification.",
                    "Monosaccharides: classification based on functional groups and number of carbon atoms.",
                    "Monosaccharide properties: esterification, oxidation, reduction, osazone formation, cyanohydrin reaction, furfural formation and enolization.",
                    "Monosaccharide derivatives: deoxy derivatives, acids, alcohols, amino sugars and sialic acid; biological importance.",
                    "Disaccharides and polysaccharides: classification and biological importance.",
                    "Lipids: definition; structure of glycerol and fatty acids; properties of fatty acids.",
                    "Kinds of lipids: glycerol lipids, lipids without glycerol and complex lipids; properties and biological roles.",
                    "Proteins: definition; amino acids and classification into essential, semi-essential and non-essential; polar and non-polar; acidic, basic and neutral.",
                    "Properties of amino acids: zwitterions; electrolytes; ninhydrin reaction; Sanger's reaction; Edman's reaction; Dansyl chloride reaction; phosgene reaction; decarboxylation; esterification and acylation.",
                    "Peptide bonds and polypeptides; primary, secondary, tertiary and quaternary structures of polypeptides.",
                    "Classification and functions of proteins.",
                    "Enzymes: properties and chemical structure; mechanism of action; denaturation; factors affecting enzyme action; allosteric proteins and feedback inhibition; classification and nomenclature.",
                    "Plant pigments: structure and functions of chlorophylls, carotenoids, anthocyanins and phycobilins.",
                    "Vitamins and their role in plants: fat-soluble vitamins A, E and K.",
                    "Water-soluble vitamins: coenzyme A and vitamins B1, B2, B6, C and H.",
                    "Introduction to bioinformatics: definition; role of computers; branches; aims; scope and research areas.",
                    "Biological data: DNA sequences, protein sequences and macromolecular structures.",
                    "Bioinformatics databases and basic tools: database searching using Entrez and SRS; BLAST and FASTA.",
                ],
            ),
            (
                "Unit B",
                "Plant Biotechnology",
                75,
                [
                    "Overview of biotechnology: origin and history.",
                    "Scope and importance of biotechnology in medicine, food industry, agriculture, fermentation technology and environmental engineering.",
                    "Achievements of biotechnology: gene cloning; recombinant DNA technology; in-vitro culture technology; genetically engineered drugs; disease diagnosis; biosensors; biofertilizers; mutation breeding; enzyme technology; DNA fingerprinting and monoclonal antibodies.",
                    "Plant tissue culture: introduction.",
                    "Principles of in-vitro culture: totipotency; basic requirements for growing plants in vitro.",
                    "Plant tissue culture laboratory organization; composition and selection of nutrient media; sterilization; culture room.",
                    "Types and applications of tissue culture: seed culture.",
                    "Organ culture: meristem culture, root culture and shoot culture.",
                    "Embryo culture, anther culture, ovule culture and endosperm culture.",
                    "Callus culture, protoplast culture and cell suspension culture.",
                    "Cryopreservation: principles.",
                    "Methods of cryopreservation: preparation of material for deep freezing; cryoprotectors; freezing programmes; storage strategies; assessment of successful cryopreservation.",
                    "Uses of cryopreservation: semen; ova and embryos; long-term maintenance of plant germplasm; organ explants; zygotic and immature embryos; shoot tips; callus; cell suspensions and protoplasts.",
                    "Significance of cryopreservation.",
                    "Plant-microbe interaction: biological nitrogen fixation, its mechanism and importance.",
                    "Symbiotic and asymbiotic organisms for soil fertility and crop improvement.",
                    "Rhizobium: nodule formation; nitrogen-fixing organisms in nodules; nodule structure and function; mechanism of nitrogen fixation; Rhizobium biofertilizers; use in forest trees.",
                    "Blue-green algae: mass production and application.",
                    "Azolla-Anabaena symbiosis; asymbiotic associations; non-symbiotic nitrogen-fixing bacteria.",
                    "Non-symbiotic bacterial biofertilizers: Azotobacter, Azospirillum and carrier formulation.",
                    "Frankia biofertilizer.",
                    "Mycorrhiza: types; benefits to plants; establishment of mycorrhizal associations in vitro.",
                    "Gene transfer in plants: concept of gene cloning and basic requirements for gene cloning in plants.",
                    "Gene isolation and cloning; concept of vectors; marker genes and reporter genes and their roles in plant transformation.",
                    "Identification and analysis of cloned genes: colony hybridization, immunological detection, PCR and blotting.",
                    "Gene transfer techniques: direct or vectorless methods and indirect or vector-mediated methods.",
                    "Transformation of mitochondria and chloroplasts.",
                    "Genetically modified crops: applications and limitations.",
                    "General concept of molecular farming from transgenic plants; ethical issues in plant genetic engineering.",
                ],
            ),
        ],
    },

    {
        "code": "RM305",
        "title": "Research Methodology",
        "category": "compulsory",
        "full_marks": 100,
        "pass_marks": "35",
        "hours": 150,
        "units": [
            (
                "Unit 1",
                "Introduction to Research",
                15,
                [
                    "1.1 Scientific methods and research: concept and definitions of research; purpose, importance, steps, levels and rigor of research; different paradigms of research.",
                    "1.2 Basic types of research: fundamental and applied; descriptive and analytical; quantitative and qualitative; conceptual and empirical; diagnostic and hypothesis testing; conclusion-oriented and decision-oriented; theoretical and action research; longitudinal and cross-sectional research.",
                    "1.3 Research questions: introduction, types and identification.",
                    "1.3 Research problems: definition, identification, ways of understanding a problem, criteria of a good problem and guidelines for selecting a meaningful problem.",
                    "1.3 Research objectives: definition, broad and specific objectives and goals.",
                    "1.3 Research hypotheses: meaning, sources, qualities of a workable hypothesis and utilities.",
                    "1.4 Designing research work: introduction, purposes and characteristics of research design; principles of designing research.",
                    "1.4 Conceptual framework and its operationalization; sectors of research design; similarities and differences between research design and research method; research methods as research designing.",
                ],
            ),
            (
                "Unit 2",
                "Some Research Methods",
                20,
                [
                    "2.1 Conventional research method: principles and importance; scientific methods as conventional methods; characteristics and aspects of scientific method; evolution of scientific studies; steps in scientific methods.",
                    "2.2 Historical research method: nature and steps; importance and fundamentals; sources of historical data; limitations.",
                    "2.3 Experimental research method: introduction; types of experiments; steps in experimental research; problems in experimentation.",
                    "2.3 Ex-post facto research: definition and technique.",
                    "2.4 Survey research method: introduction and importance; comparison with other methods.",
                    "2.4 Objectives and types of social surveys and technical surveys; steps in social and technical surveys; pilot survey.",
                    "2.5 Case study: introduction; exploratory and hypothesis-testing case studies; steps; sources of case data; limitations.",
                ],
            ),
            (
                "Unit 3",
                "Data and Methods of Data Collection",
                20,
                [
                    "3.1 Needs and nature of data: necessity in natural, physical, biological and social sciences; nature of data in natural and social sciences.",
                    "3.1 Forms of information: primary and secondary data; cross-section and categorical data; time-series, spatial and ordered data.",
                    "3.2 Types of data according to measurement scales: qualitative and quantitative; nominal, ordinal, interval and ratio scale data.",
                    "3.3 Schedule: purpose, kinds, content and limitations.",
                    "3.3 Questionnaire: types; requisites of a good questionnaire; importance and limitations; difference between schedule and questionnaire; format and problems.",
                    "3.3 Interviews: direct and indirect interviews; ways of obtaining an interview; focus group discussion.",
                    "3.3 Survey and census: introduction; similarities and differences; methods of sampling human populations.",
                    "3.3 Observation methods: participatory and non-participatory observation; PRA and RRA; controls used in social surveys; observational documents and their types.",
                    "3.4 Data collection in laboratory-oriented sciences and technologies: introduction; methods in natural sciences; data measurement and observation.",
                    "3.4 Observation schedule, observation plan, check sheet, rating scale and Likert scale.",
                    "3.4 Controlled and non-controlled observation.",
                    "3.4 Sample and specimen; sampling of objects or beings; anonymity, confidentiality and informed consent in research ethics.",
                    "3.4 Observational method versus experimental method.",
                    "3.5 Non-response: causes; estimation of non-response rate; techniques for obtaining responses; random response technique.",
                    "3.6 Questions: types of questions; questions to be avoided; sequence of questions in schedules, questionnaires and interviews.",
                ],
            ),
            (
                "Unit 4",
                "Sampling",
                10,
                [
                    "4.1 Introduction and review of sampling: definition, needs and steps.",
                    "4.1 Definitions of population, sample, sampling unit, sampling frame, sampling error and non-sampling error.",
                    "4.1 Steps, fundamentals, characteristics, advantages and disadvantages of sampling.",
                    "4.2 Probability sampling: simple, stratified, systematic, cluster and multistage sampling; process of selecting random samples.",
                    "4.2 Non-probability sampling: convenience, purposive, quota, snowball and self-selecting sampling; advantages and disadvantages.",
                    "4.3 Sample size: factors affecting sample size; testing sample reliability; methods of estimating sample size; process of selecting random samples.",
                ],
            ),
            (
                "Unit 5",
                "Data Analysis and Synthesis",
                20,
                [
                    "5.1 Data organization and summarization: editing, coding, classification and entering data into spreadsheets.",
                    "5.1 Management of missing and inconsistent information.",
                    "5.2 Principal methods of analysis and interpretation.",
                    "5.2 Descriptive statistical measures: concentration, spread and comparison of spread.",
                    "5.2 Identifying the nature of curves and distributions.",
                    "5.2 Estimation of population parameters and standard error.",
                    "5.2 Hypothesis testing and variance analysis (brief review of B.Sc. Second Year Applied Statistics).",
                    "5.3 Synthesis: meaning and introduction; logical generalization and statistical generalization.",
                ],
            ),
            (
                "Unit 6",
                "Measurement and Scaling",
                20,
                [
                    "6.1 Review of measurement and scales: concepts, types and sources of measurement error.",
                    "6.1 Needs of scaling and characteristics of a scale.",
                    "6.2 Reliability: definition; methods of estimating reliability; test length and reliability; reliability theory; estimation of true score.",
                    "6.3 Validity: introduction to validity of scale; types of validity; factors influencing validity; validity theory and measures of validity.",
                    "6.3 Validity and test length; general criteria of validity of a scale.",
                    "6.4 Scaling: scores and scales; scaling of scores; difficulties in scaling.",
                    "6.4 Scales used in physical and social sciences (introduction only).",
                    "6.4 Standard scores and standard scales: Z scale, sigma scale, T scale, percentile scale and ranking scales.",
                ],
            ),
            (
                "Unit 7",
                "Task of Writing in Research",
                20,
                [
                    "7.1 Research proposal: meaning and purpose; academic, project and case-study proposals.",
                    "7.1 Steps for preparing a proposal; framework and arrangement of subheadings.",
                    "7.1 Writing a research proposal for an academic programme; common mistakes in proposal writing.",
                    "7.2 Reviewing literature and note taking: methods of selecting relevant literature; ways of note taking and recording from different sources.",
                    "7.3 Research report: introduction, purpose and different forms; qualities of research reports.",
                    "7.3 Presentation of preliminary, general and technical reports; format; necessary elements; precautions for report preparation.",
                    "7.4 Thesis and dissertation: introduction; features; structure; steps in thesis writing; documentation.",
                    "7.5 Citation and referencing: ways of citing work; arranging reference material; bibliography; quoting from different sources.",
                    "7.5 Citation and referencing systems: APA, MLA and ISO 690 numerical referencing.",
                    "7.6 Publication in research journals: introduction and importance; arrangement of an article; differences between general and research articles.",
                ],
            ),
            (
                "Assignment",
                "Assignment Works and Exercises",
                25,
                [
                    "Preparation of a research or project proposal.",
                    "Questionnaire designing.",
                    "Preparation of an observation schedule for field or laboratory work.",
                    "Case analysis and situation analysis.",
                    "Survey report preparation or field/laboratory work report preparation.",
                    "Presentation on a related topic (class seminar).",
                    "Analysis of references and citations from books, journals, reports and theses.",
                ],
            ),
        ],
    },

    {
        "code": "CHE303",
        "title": "Basic Biochemistry",
        "category": "elective",
        "full_marks": 50,
        "pass_marks": "17.5",
        "hours": 75,
        "units": [
            (
                "Unit 1",
                "Biochemistry Foundations",
                3,
                [
                    "Biochemistry: definition, short history and applications.",
                    "pH scale and pH of biological fluids.",
                    "Henderson-Hasselbalch equation and its importance.",
                    "Biologically important buffers.",
                ],
            ),
            (
                "Unit 2",
                "Nucleic Acids",
                22,
                [
                    "Nucleotides: building blocks of nucleic acids; characteristic bases and pentoses.",
                    "Phosphodiester bonds linking successive nucleotides in nucleic acids.",
                    "Nucleic acid structure; DNA as the storage molecule of genetic information.",
                    "Distinctive base composition and properties of DNA molecules.",
                    "Double-helical structure of DNA and different three-dimensional forms.",
                    "DNA biosynthesis and replication.",
                    "RNA biosynthesis and transcription.",
                    "Genetic code and codons.",
                    "Mutation: non-enzymatic transformation of nucleotides and nucleic acids; mutants.",
                    "DNA repair.",
                    "DNA sequencing: Frederick Sanger method.",
                    "Recombinant DNA technology; DNA cloning; restriction endonucleases and DNA ligase.",
                    "Cloning vectors and amplification of inserted DNA segments.",
                    "Polymerase chain reaction (PCR): amplification of specific DNA sequences and applications.",
                    "Biological functions of DNA and RNA; biosynthesis and repair of DNA and mRNA.",
                    "DNA polymorphism, genetic diseases and Human Genome Project.",
                ],
            ),
            (
                "Unit 3",
                "Amino Acids, Peptides and Proteins",
                15,
                [
                    "Amino acids: common structural features and L-stereoisomers in proteins.",
                    "Classification of amino acids according to R groups.",
                    "Uncommon amino acids with important functions and amino acids not found in proteins.",
                    "Amino acid degradation: oxidative deamination, transamination and decarboxylation.",
                    "Functions of pyridoxal phosphate (PLP).",
                    "Biosynthesis of glycine, methionine, serine and tyrosine.",
                    "Amino acid sequencing: terminal group analysis and Edman N-terminal sequencing.",
                    "Quantitative estimation of proteins by SDS-PAGE.",
                ],
            ),
            (
                "Unit 4",
                "Enzymes",
                12,
                [
                    "Enzymes: definition, properties and terminology.",
                    "Coenzymes, cofactors and prosthetic groups.",
                    "Enzyme kinetics and Michaelis-Menten equation.",
                    "Transformations of the Michaelis-Menten equation.",
                    "Lineweaver-Burk and Eadie-Hofstee plots.",
                    "Enzyme inhibition: competitive, noncompetitive and uncompetitive inhibition.",
                    "Effects of pH, temperature, substrate concentration and incubation time on enzyme action.",
                    "Mechanism of enzyme action: lock-and-key and induced-fit models.",
                    "Regulation of enzyme activity.",
                    "Enzymes of industrial and clinical diagnostic importance.",
                ],
            ),
            (
                "Unit 5",
                "Carbohydrates",
                8,
                [
                    "Glycogenesis and gluconeogenesis.",
                    "Glycolysis and its relationship with respiration.",
                    "Tricarboxylic acid (TCA) cycle.",
                    "Pentose phosphate pathway.",
                    "Principles of bioenergetics.",
                    "Electron transport system and oxidative phosphorylation.",
                ],
            ),
            (
                "Unit 6",
                "Lipids",
                15,
                [
                    "Definition and classification of lipids: natural lipids, fats, waxes, soaps, phospholipids, glycolipids and steroids.",
                    "Saponification number, iodine value and acid number.",
                    "Rancidity and auto-oxidation.",
                    "Fatty acids: saturated and unsaturated fatty acids.",
                    "Fatty acid metabolism: beta-oxidation.",
                    "Biosynthesis of fatty acids, including palmitic acid.",
                    "Biosynthesis of lipids, including tripalmitin.",
                    "Cholesterol biosynthesis and bile salts derived from cholesterol.",
                    "Theories of fat absorption.",
                    "Prostanoids, eicosanoids and leukotrienes.",
                    "Lipoxygenase and cyclooxygenase pathways.",
                ],
            ),
        ],
    },

    {
        "code": "BOT304",
        "title": "Medicinal and Aromatic Plants",
        "category": "elective",
        "full_marks": 50,
        "pass_marks": "17.5",
        "hours": 75,
        "units": [
            (
                "Unit 1",
                "Overview and Importance",
                7,
                [
                    "Introduction and definitions of non-timber forest products (NTFPs).",
                    "Definitions of medicinal and aromatic plants (MAPs).",
                    "Historical perspectives and current use of MAPs.",
                    "Importance of MAPs in traditional medicinal practices: Ayurvedic, Unani, Amchi/Tibetan and homeopathy.",
                    "Future prospects and introduction to bioprospecting.",
                    "MAPs, traditional knowledge and drug development.",
                    "Intellectual property rights (IPR) and biopiracy.",
                ],
            ),
            (
                "Unit 2",
                "Diversity, Distribution and Trade Potentials",
                6,
                [
                    "Diversity and distribution patterns of NTFPs and MAPs in various climatic zones of Nepal.",
                    "Factors affecting distribution of NTFPs and MAPs.",
                    "Trade potentials of NTFPs and MAPs in Nepal.",
                    "Major trends in NTFP and MAP trade.",
                    "Role of NTFPs and MAPs in the promotion of people's livelihoods.",
                ],
            ),
            (
                "Unit 3",
                "Conservation Status and Sustainable Use",
                12,
                [
                    "Conservation status of MAPs: major conservation issues and threats.",
                    "MAPs of Nepal in the IUCN Red List, CITES appendices and government protection list.",
                    "Conservation and sustainable use: major principles, opportunities and constraints.",
                    "Dimensions of MAP sustainability.",
                    "In-situ and ex-situ conservation strategies.",
                    "Alternatives to wild harvesting and eco-certification processes.",
                    "Community-based management.",
                    "National policies and programmes for promotion of the MAP sector in Nepal.",
                ],
            ),
            (
                "Unit 4",
                "Pharmacognosy",
                8,
                [
                    "Concept and scope of pharmacognosy.",
                    "Crude drug production of MAPs.",
                    "Techniques for extraction of major phytochemicals from MAPs.",
                    "Distillation technology for essential oils.",
                    "Quality control.",
                    "Herbal cosmetics, potentiality of herbal drugs and herbal-based industries.",
                ],
            ),
            (
                "Unit 5",
                "Cultivation Technologies of Commercially Important MAPs",
                25,
                [
                    "Introduction: opportunities and constraints in cultivation and production of MAPs in Nepal.",
                    "Asparagus racemosus: traditional and commercial uses, active constituents, distribution, climate and soil requirements, cultivation, harvesting and post-harvest technologies.",
                    "Azadirachta indica: uses, active constituents, distribution, climate and soil requirements, cultivation, harvesting and post-harvest technologies.",
                    "Neopicrorhiza scrophulariiflora: uses, active constituents, distribution, climate and soil requirements, cultivation, harvesting and post-harvest technologies.",
                    "Paris polyphylla: uses, active constituents, distribution, climate and soil requirements, cultivation, harvesting and post-harvest technologies.",
                    "Phyllanthus emblica: uses, active constituents, distribution, climate and soil requirements, cultivation, harvesting and post-harvest technologies.",
                    "Piper longum: uses, active constituents, distribution, climate and soil requirements, cultivation, harvesting and post-harvest technologies.",
                    "Rheum australe: uses, active constituents, distribution, climate and soil requirements, cultivation, harvesting and post-harvest technologies.",
                    "Sapindus mukorossi: uses, active constituents, distribution, climate and soil requirements, cultivation, harvesting and post-harvest technologies.",
                    "Swertia chirayita: uses, active constituents, distribution, climate and soil requirements, cultivation, harvesting and post-harvest technologies.",
                    "Taxus wallichiana: uses, active constituents, distribution, climate and soil requirements, cultivation, harvesting and post-harvest technologies.",
                    "Valeriana jatamansii: uses, active constituents, distribution, climate and soil requirements, cultivation, harvesting and post-harvest technologies.",
                    "Zanthoxylum armatum: uses, active constituents, distribution, climate and soil requirements, cultivation, harvesting and post-harvest technologies.",
                    "Cultivation technologies: propagation and nursery techniques; transplantation of seedlings and rooted cuttings; irrigation techniques; disease and pest management.",
                    "Harvesting and post-harvest technologies: processing, value addition and major trade issues.",
                ],
            ),
            (
                "Unit 6",
                "Harvesting Technologies of Commercially Important MAPs",
                12,
                [
                    "Harvest and post-harvest technologies: harvesting periods and methods of sustainable harvesting.",
                    "Processing and value addition.",
                    "Marketing and value-chain analysis.",
                    "Major trade issues.",
                    "Cordyceps sinensis: active constituents and uses.",
                    "Dactylorrhiza hatagirea: active constituents and uses.",
                    "Hippophae species: active constituents and uses.",
                    "Morchella species: active constituents and uses.",
                    "Nardostachys grandiflora: active constituents and uses.",
                    "Podophyllum hexandrum: active constituents and uses.",
                ],
            ),
            (
                "Unit 7",
                "Field Visit and Report Writing",
                5,
                [
                    "Field visit to a herbal farm.",
                    "Field visit to a herbal industry.",
                    "Field observation and report writing.",
                ],
            ),
        ],
    },
]


# Explicit grouping only: original syllabus text is retained.

# Logical lesson headings for all five subjects.
# Each range is inclusive and refers to the original topic indexes,
# starting from zero in the COURSES list.

LESSON_GROUPS = {
    # CHE301 - General Chemistry I

    ("CHE301", "Group A"): [
        ("Hydrogen and Noble Gases", 0, 1),
        ("Boron and Silicon Compounds", 2, 3),
        ("Halogen Compounds", 4, 4),
        ("Electronegativity and Periodic Properties", 5, 6),
        ("Chemical Fertilizers and Nitrogen Fixation", 7, 8),
        ("Environmental Pollution", 9, 12),
    ],

    ("CHE301", "Group B"): [
        ("Organic Reaction Fundamentals", 0, 2),
        ("Reactive Intermediates", 3, 4),
        ("Free Radical Chemistry", 5, 6),
        ("Spectroscopy", 7, 10),
        ("Heterocyclic Chemistry", 11, 13),
    ],

    ("CHE301", "Group C"): [
        ("Electrolytic Conductance and Activity", 0, 1),
        ("Electrochemical Cells", 2, 4),
        ("Applications of EMF Measurements", 5, 5),
        ("Molecular Spectroscopy", 6, 10),
        ("Polymer Chemistry", 11, 12),
        ("Entropy and Thermodynamic Functions", 13, 14),
        ("Thermodynamic Equilibrium", 15, 16),
    ],

    # BOT301 - Plant Biochemistry and Biotechnology

    ("BOT301", "Unit A"): [
        ("Introduction to Plant Biochemistry", 0, 1),
        ("Water and Biological Functional Groups", 2, 3),
        ("Carbohydrates", 4, 8),
        ("Lipids", 9, 10),
        ("Amino Acids and Proteins", 11, 15),
        ("Plant Pigments", 16, 16),
        ("Vitamins in Plants", 17, 18),
        ("Introduction to Bioinformatics", 19, 20),
        ("Bioinformatics Databases and Tools", 21, 21),
    ],

    ("BOT301", "Unit B"): [
        ("Introduction and Scope of Biotechnology", 0, 2),
        ("Fundamentals of Plant Tissue Culture", 3, 5),
        ("Types of Plant Tissue Culture", 6, 9),
        ("Cryopreservation", 10, 13),
        ("Plant-Microbe Interactions and Nitrogen Fixation", 14, 21),
        ("Plant Gene Cloning and Transformation", 22, 26),
        ("Genetically Modified Crops and Molecular Farming", 27, 28),
    ],

    # RM305 - Research Methodology

    ("RM305", "Unit 1"): [
        ("Scientific Methods and Research", 0, 1),
        ("Research Questions, Problems and Objectives", 2, 4),
        ("Research Hypotheses", 5, 5),
        ("Research Design and Conceptual Framework", 6, 7),
    ],

    ("RM305", "Unit 2"): [
        ("Conventional Research Methods", 0, 0),
        ("Historical Research", 1, 1),
        ("Experimental and Ex-post Facto Research", 2, 3),
        ("Survey Research", 4, 5),
        ("Case Study Method", 6, 6),
    ],

    ("RM305", "Unit 3"): [
        ("Nature and Forms of Research Data", 0, 1),
        ("Types and Measurement Scales of Data", 2, 2),
        ("Schedules, Questionnaires and Interviews", 3, 5),
        ("Survey, Census and Observation Methods", 6, 7),
        ("Laboratory Data Collection and Measurement", 8, 13),
        ("Non-response and Questionnaire Design", 14, 14),
    ],

    ("RM305", "Unit 4"): [
        ("Fundamentals of Sampling", 0, 2),
        ("Probability and Non-probability Sampling", 3, 4),
        ("Sample Size and Reliability", 5, 5),
    ],

    ("RM305", "Unit 5"): [
        ("Data Organization and Management", 0, 1),
        ("Data Analysis and Interpretation", 2, 6),
        ("Synthesis and Generalization", 7, 7),
    ],

    ("RM305", "Unit 6"): [
        ("Measurement and Scaling Fundamentals", 0, 1),
        ("Reliability of Measurement Scales", 2, 2),
        ("Validity of Measurement Scales", 3, 4),
        ("Scaling and Standard Scores", 5, 7),
    ],

    ("RM305", "Unit 7"): [
        ("Research Proposal Writing", 0, 2),
        ("Literature Review and Note Taking", 3, 3),
        ("Research Report Preparation", 4, 5),
        ("Thesis and Dissertation Writing", 6, 6),
        ("Citation, Referencing and Publication", 7, 9),
    ],

    ("RM305", "Assignment"): [
        ("Research Proposal and Questionnaire", 0, 1),
        ("Observation and Case Analysis", 2, 3),
        ("Research Reporting and Presentation", 4, 5),
        ("References and Citations", 6, 6),
    ],

    # CHE303 - Basic Biochemistry

    ("CHE303", "Unit 1"): [
        ("Introduction to Biochemistry", 0, 0),
        ("pH, Buffers and Biological Fluids", 1, 3),
    ],

    ("CHE303", "Unit 2"): [
        ("Nucleotide Structure and Nucleic Acids", 0, 4),
        ("DNA Replication and RNA Transcription", 5, 6),
        ("Genetic Code and Mutation", 7, 8),
        ("DNA Repair and Sequencing", 9, 10),
        ("Recombinant DNA Technology", 11, 13),
        ("Biological Functions of Nucleic Acids", 14, 15),
    ],

    ("CHE303", "Unit 3"): [
        ("Amino Acid Structure and Classification", 0, 2),
        ("Amino Acid Degradation and PLP", 3, 4),
        ("Amino Acid Biosynthesis", 5, 5),
        ("Protein Sequencing and Estimation", 6, 7),
    ],

    ("CHE303", "Unit 4"): [
        ("Enzyme Fundamentals and Cofactors", 0, 1),
        ("Enzyme Kinetics", 2, 4),
        ("Enzyme Inhibition", 5, 5),
        ("Factors Affecting Enzyme Activity", 6, 6),
        ("Mechanism and Regulation of Enzyme Action", 7, 8),
        ("Industrial and Clinical Enzymes", 9, 9),
    ],

    ("CHE303", "Unit 5"): [
        ("Carbohydrate Metabolism", 0, 3),
        ("Bioenergetics and Oxidative Phosphorylation", 4, 5),
    ],

    ("CHE303", "Unit 6"): [
        ("Classification and Properties of Lipids", 0, 2),
        ("Fatty Acids and Their Metabolism", 3, 4),
        ("Biosynthesis of Fatty Acids and Lipids", 5, 6),
        ("Cholesterol and Bile Salts", 7, 7),
        ("Fat Absorption", 8, 8),
        ("Eicosanoids and Lipid Pathways", 9, 10),
    ],

    # BOT304 - Medicinal and Aromatic Plants

    ("BOT304", "Unit 1"): [
        ("Introduction to NTFPs and MAPs", 0, 2),
        ("Traditional Uses and Importance of MAPs", 3, 5),
        ("Intellectual Property Rights and Biopiracy", 6, 6),
    ],

    ("BOT304", "Unit 2"): [
        ("Diversity and Distribution of MAPs", 0, 1),
        ("Trade Potential and Economic Importance", 2, 4),
    ],

    ("BOT304", "Unit 3"): [
        ("Conservation Status and Threats", 0, 1),
        ("Sustainable Use and Conservation Principles", 2, 3),
        ("In-situ and Ex-situ Conservation", 4, 5),
        ("Community Management and National Policies", 6, 7),
    ],

    ("BOT304", "Unit 4"): [
        ("Introduction to Pharmacognosy", 0, 1),
        ("Extraction and Distillation Technologies", 2, 3),
        ("Quality Control and Herbal Industries", 4, 5),
    ],

    ("BOT304", "Unit 5"): [
        ("Introduction to Commercial MAP Cultivation", 0, 0),
        ("Cultivation of Commercially Important MAP Species", 1, 12),
        ("Cultivation and Nursery Technologies", 13, 13),
        ("Harvesting and Post-harvest Technologies", 14, 14),
    ],

    ("BOT304", "Unit 6"): [
        ("Harvesting and Post-harvest Technologies", 0, 3),
        ("Commercially Important MAP Species", 4, 9),
    ],

    ("BOT304", "Unit 7"): [
        ("Field Visits and Practical Observation", 0, 1),
        ("Field Observation and Report Writing", 2, 2),
    ],
}


def get_or_create_official_unit(subject, sequence, code, title, hours):
    unit = Unit.objects.filter(
        subject=subject,
        code=code,
        is_custom=False,
    ).first()

    if unit is None:
        unit = Unit.objects.filter(
            subject=subject,
            sequence=sequence,
            is_custom=False,
        ).first()

    if unit is not None:
        unit.code = code
        unit.title = title
        unit.sequence = sequence
        unit.lecture_hours = hours
        unit.save(
            update_fields=[
                "code",
                "title",
                "sequence",
                "lecture_hours",
            ]
        )
        return unit

    actual_sequence = sequence

    if Unit.objects.filter(
        subject=subject,
        sequence=actual_sequence,
    ).exists():
        actual_sequence = (
            Unit.objects.filter(subject=subject)
            .order_by("-sequence")
            .values_list("sequence", flat=True)
            .first() or 0
        ) + 1

    return Unit.objects.create(
        subject=subject,
        code=code,
        title=title,
        sequence=actual_sequence,
        lecture_hours=hours,
        is_custom=False,
    )


def update_official_topics(unit, topics, hours, course_code):
    """
    Organize official syllabus entries into meaningful lessons.

    - Original syllabus wording is retained.
    - Lesson headings are parent topics.
    - Original syllabus entries are child topics.
    - Unit teaching minutes are distributed across leaf topics.
    - Custom topics are not deleted.
    """

    groups = LESSON_GROUPS.get(
        (course_code, unit.code),
        [],
    )

    # Validate group ranges and ensure every syllabus entry
    # belongs to no more than one group.
    grouped_indexes = set()

    hierarchy = []

    for lesson_title, first_index, last_index in groups:
        if first_index < 0 or last_index >= len(topics):
            raise ValueError(
                f"Invalid lesson range in {course_code} "
                f"{unit.code}: {lesson_title}"
            )

        if first_index > last_index:
            raise ValueError(
                f"Invalid range for lesson: {lesson_title}"
            )

        indexes = list(range(first_index, last_index + 1))

        overlap = grouped_indexes.intersection(indexes)
        if overlap:
            raise ValueError(
                f"Overlapping lesson groups in {course_code} "
                f"{unit.code}: {lesson_title}"
            )

        grouped_indexes.update(indexes)

        hierarchy.append({
            "title": lesson_title,
            "children": [topics[i] for i in indexes],
            "position": first_index,
        })

    # Entries not included in a group remain standalone lessons.
    for index, title in enumerate(topics):
        if index not in grouped_indexes:
            hierarchy.append({
                "title": title,
                "children": [],
                "position": index,
            })

    hierarchy.sort(key=lambda item: item["position"])

    # Teaching time is distributed among original syllabus
    # entries, never among parent lesson headings.
    leaf_count = len(topics)
    total_minutes = int(hours or 0) * 60

    if leaf_count:
        base_minutes, extra_minutes = divmod(
            total_minutes,
            leaf_count,
        )
    else:
        base_minutes, extra_minutes = 0, 0

    next_sequence = (
        Topic.objects.filter(unit=unit)
        .order_by("-sequence")
        .values_list("sequence", flat=True)
        .first() or 0
    )

    leaf_index = 0

    def get_official_topic(title):
        return Topic.objects.filter(
            unit=unit,
            title=title,
            is_custom=False,
        ).first()

    def get_or_create_topic(title, parent=None):
        nonlocal next_sequence

        topic = get_official_topic(title)

        if topic is None:
            next_sequence += 1

            topic = Topic.objects.create(
                unit=unit,
                title=title,
                sequence=next_sequence,
                estimated_minutes=0,
                is_custom=False,
                parent=parent,
            )
        else:
            topic.parent = parent
            topic.save(update_fields=["parent"])

        return topic

    def allocate_minutes():
        nonlocal leaf_index

        minutes = base_minutes

        if leaf_index < extra_minutes:
            minutes += 1

        leaf_index += 1
        return minutes

    for item in hierarchy:
        lesson_title = item["title"]
        children = item["children"]

        if children:
            parent = get_or_create_topic(
                lesson_title,
                parent=None,
            )

            parent.estimated_minutes = 0
            parent.save(
                update_fields=["estimated_minutes"]
            )

            for child_title in children:
                child = get_or_create_topic(
                    child_title,
                    parent=parent,
                )

                child.estimated_minutes = allocate_minutes()
                child.save(
                    update_fields=[
                        "estimated_minutes",
                        "parent",
                    ]
                )

        else:
            topic = get_or_create_topic(
                lesson_title,
                parent=None,
            )

            topic.estimated_minutes = allocate_minutes()
            topic.save(
                update_fields=[
                    "estimated_minutes",
                    "parent",
                ]
            )

    # Check that the complete unit duration is preserved.
    allocated = sum(
        topic.estimated_minutes
        for topic in Topic.objects.filter(
            unit=unit,
            is_custom=False,
            subtopics__isnull=True,
        ).distinct()
    )

    if allocated != total_minutes:
        raise ValueError(
            f"Duration mismatch for {course_code} "
            f"{unit.code}: expected {total_minutes}, "
            f"allocated {allocated}"
        )


class Command(BaseCommand):
    help = (
        "Create and update the five selected TU B.Sc. "
        "Third Year theory syllabus papers."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        for subject_order, course in enumerate(COURSES, 1):
            subject, created = Subject.objects.get_or_create(
                code=course["code"],
                defaults={
                    "title": course["title"],
                    "category": course["category"],
                    "full_marks": course["full_marks"],
                    "pass_marks": course["pass_marks"],
                    "lecture_hours": course["hours"],
                    "year": 3,
                    "syllabus_source": SOURCE,
                    "syllabus_version": VERSION,
                    "sort_order": subject_order,
                    "is_active": True,
                },
            )

            subject.title = course["title"]
            subject.category = course["category"]
            subject.full_marks = course["full_marks"]
            subject.pass_marks = course["pass_marks"]
            subject.lecture_hours = course["hours"]
            subject.year = 3
            subject.syllabus_source = SOURCE
            subject.syllabus_version = VERSION
            subject.sort_order = subject_order
            subject.is_active = True
            subject.save()

            for unit_sequence, unit_data in enumerate(
                course["units"],
                1,
            ):
                unit_code, unit_title, hours, topics = unit_data

                unit = get_or_create_official_unit(
                    subject=subject,
                    sequence=unit_sequence,
                    code=unit_code,
                    title=unit_title,
                    hours=hours,
                )

                update_official_topics(
                    unit=unit,
                    topics=topics,
                    hours=hours,
                    course_code=course["code"],
                )

            action = "Created" if created else "Updated"

            self.stdout.write(
                self.style.SUCCESS(
                    f"{action}: {subject.code} - {subject.title}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                "All five theory syllabus subjects have been seeded."
            )
        )

        self.stdout.write(
            self.style.WARNING(
                "Existing custom records were preserved. "
                "Unused old official topics were not deleted."
            )
        )

        self.stdout.write(
            self.style.WARNING(
                "Only the explicitly configured lesson groupings "
                "have been nested. Other syllabus entries remain "
                "individual topics."
            )
        )
