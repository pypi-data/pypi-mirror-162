from persona_export.exports import FacebookExporter, SalesForceMarketingCloudExporter, \
    DataPlatformExporter, DummyExporter, Connectors, HistorizedInsightExporter, FacebookManualExporter


class ServiceProvider:
    AVAILABLE_SERVICE = {
        "facebook_api": FacebookExporter.FacebookExporter,
        "facebook": FacebookManualExporter.FacebookManualExporter,
        "salesforce": SalesForceMarketingCloudExporter.SalesForceMarketingCloudExporter,
        "data_platform": DataPlatformExporter.DataPlatformExporter,
        "app": Connectors.Connectors,
        "insights": HistorizedInsightExporter.Insights
    }

    DUMMY_SERVICE = DummyExporter.DummyExporter

    @classmethod
    def get(cls, name: str, throw_exception=False):
        """ Return obtained service, if not available, return dummy service

            :param name: name of service
            :param throw_exception: true to raise exception when service is not available
            :type throw_exception bool
            :raise ModuleNotFoundError when service not available
        """
        if throw_exception and (name not in cls.AVAILABLE_SERVICE):
            raise ModuleNotFoundError

        # when service not available, return dummy
        return cls.AVAILABLE_SERVICE.get(name, cls.DUMMY_SERVICE)
