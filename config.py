from skabenclient.config import DeviceConfigExtended

ESSENTIAL = {
        'minimal': 'boilerplate'        
}

# DeviceConfigExtended supports file and json download and management
# use DeviceConfig if you don't need this functionality


class BoilerplateConfig(DeviceConfigExtended):

    def __init__(self, config):
        self.minimal_essential_conf = ESSENTIAL
        super().__init__(config)

    def save(self, data=None):
        # <-- add here your specific config serializing
        return super().save()

    def load(self):
        # <-- add here your specific config deserializing
        return super().load()
