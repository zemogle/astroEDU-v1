from django.db.models import Q
import logging

logger = logging.getLogger('spaceawe')


class SearchModel(object):

    #search_fields = ('title', 'teaser', 'story',)
    #article_search_fields = ('title', 'teaser', 'fulldesc',)

    @classmethod
    def get_query(cls, query_string, search_fields, filters={}):
        query = Q()
        for field in search_fields:
            query |= Q(**{'translations__%s__icontains' % field: query_string})
        all_filters = Q()
        logger.info("Get query")
        for filter_name in filters.keys():
            logger.info('Filter name %s' % filter_name)
            filter_query = Q()
            logger.info('Filters %s' % filters[filter_name])
            if filter_name == 'category':
                logger.info('category')
                for f in filters[filter_name]:
                    # category filter behaves differently than other filters
                        logger.info('Filter category %s' % f)
                        filter_query |= Q(**{'%s__exact' % f: True})
                        logger.info("filter QUERY %s" % filter_query)
            else:
                logger.info(filter_name)
                for f in filters[filter_name]:
                    logger.info('Filter %s %s' % (filter_name, f))
                    logger.info("QUERY %s" % Q({'%s__code' % filter_name: f}))
                    filter_query |= Q(**{'%s__exact' % filter_name: f})
                    logger.info("filter QUERY %s" % filter_query)

            all_filters &= filter_query
            logger.info("all filters QUERY %s" % all_filters)
        query &= all_filters
        logger.info("final QUERY %s" % query)
        return query

    @classmethod
    def search(cls, query_string, search_fields=('title', 'teaser', 'story',), filters={}):
        if not query_string:
            return []
        query = cls.get_query(query_string, search_fields, filters)
        objects = list(cls.objects.filter(query).distinct())
        return objects
