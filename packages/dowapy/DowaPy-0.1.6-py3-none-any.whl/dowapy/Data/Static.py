DefaultCommandFilter = '[ Command :: DowaPy ]'
DefaultLogFilter = '[ Log :: DowaPy ]'

# ExportMetaDataColumns = ['ScenePath', 'ExportPath', 'ShoudSerialize', 'ExportPresetPath', 'FileNameForm', 'UseGimberSolver', 'Keywords']

ExportMetaDataPathsColumns = ['ScenePath', 'ExportPath']
ExportMetaDataExportOptionsColumns = ['ExportPresetPath', 'UseGimberSolver']
ExportMetaDataNameColumns = ['ShoudSerialize', 'NameForm']
ExportMetaDataKeywordsColumns = ['CharacterMain', 'CharacterModel', 'CharacterJoint', 'PropMain', 'PropModel', 'PropJoint', 'Camera']
ExportMetaDataColumns = ['Index'] + ExportMetaDataPathsColumns + ExportMetaDataNameColumns + ExportMetaDataExportOptionsColumns + ExportMetaDataKeywordsColumns
