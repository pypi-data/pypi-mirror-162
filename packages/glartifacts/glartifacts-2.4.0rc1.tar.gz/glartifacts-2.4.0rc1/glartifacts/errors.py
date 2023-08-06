class GitlabArtifactsError(Exception):
    pass

class NoProjectError(GitlabArtifactsError):
    def __init__(self, project_path):
        super().__init__(
            'Invalid project "{}"'.format(project_path)
            )

class InvalidConfigSectionError(GitlabArtifactsError):
    def __init__(self, config_file, section_name):
        super().__init__(
            '{}: Invalid config section "{}"'.format(
                config_file,
                section_name
                )
            )

class InvalidConfigOptionError(GitlabArtifactsError):
    def __init__(self, config_file, section_name, item_name):
        super().__init__(
            '{}: Invalid config option "{}.{}"'.format(
                config_file,
                section_name,
                item_name
                )
            )

class InvalidCIConfigError(GitlabArtifactsError):
    def __init__(self, ref):
        super().__init__(
            'Invalid .gitlab-ci.yml for "{}"'.format(
                ref.tree_path()
                )
            )
