from sqlalchemy.orm import UserDefinedOption


class SetShardSchemaOption(UserDefinedOption):
    propagate_to_loaders = True

    def _gen_cache_key(self, anon_map, bindparams):
        return (self.payload,)


class SetShardEngineOption(UserDefinedOption):
    propagate_to_loaders = True

    def _gen_cache_key(self, anon_map, bindparams):
        return (self.payload,)
