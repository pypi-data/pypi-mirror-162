import time
from multiprocessing import Process
from django.db import transaction
from django import db
import sys
from django.contrib.postgres.search import SearchVector
import traceback


class RebuildWikiConfigs:
    def run(self):
        from torque import models

        for config in models.WikiConfig.objects.filter(search_cache_dirty=True).all():
            # We do this outside of the transaction, because if someone comes
            # along and dirties it again while we're rebuilding, we want to
            # rebuild it after we're done rebuilding it.
            config.search_cache_dirty = False
            config.save()
            print(
                "Rebuilding search index for %s: %s"
                % (config.wiki.wiki_key, config.group)
            )
            with transaction.atomic():
                config.rebuild_search_index()


class RebuildTOCs:
    def run(self):
        from torque import models

        for toc_cache in models.TableOfContentsCache.objects.filter(dirty=True).all():
            # As above, we do this outside of the transaction, because if someone comes
            # along and dirties it again while we're rebuilding, we want to
            # rebuild it after we're done rebuilding it.
            print(
                "Rebuilding toc %s (%s): %s..."
                % (
                    toc_cache.toc.collection.name,
                    toc_cache.wiki_config.group,
                    toc_cache.toc.name,
                ),
                end="",
            )
            toc_cache.dirty = False
            toc_cache.save()
            with transaction.atomic():
                toc_cache.rebuild()
            print("Rebuilt")


class RebuildSearchCacheDocuments:
    def run(self):
        from torque import models

        num = models.SearchCacheDocument.objects.filter(dirty=True).count()
        if num > 0:
            print("Rebuilding %s search cache documents" % num)

        for cache_document in models.SearchCacheDocument.objects.filter(dirty=True):
            collection = cache_document.document.collection
            for config in collection.configs.all():
                document_dict = cache_document.document.to_dict(config)
                cache_document.data = " ".join(list(map(str, document_dict.values())))
                cache_document.dirty = False
                cache_document.save()
                models.SearchCacheDocument.objects.filter(id=cache_document.id).update(
                    data_vector=SearchVector("data")
                )


class RebuildTemplateCacheDocuments:
    def run(self):
        from torque import models

        for template in models.Template.objects.filter(dirty=True).all():
            template.dirty = False
            template.save()

            # Right now, CSV Templates affect the template cache, and TOC templates
            # affect the ToC cache.  Others we just pass on.
            #
            # We mark it as clean even if it's another type, just so things are clean if
            # we end up adding other template types later
            if template.type == "CSV":
                for config in template.wiki.configs.all():
                    print(
                        "Rebuilding template %s (%s) for %s: %s"
                        % (
                            template.name,
                            template.type,
                            config.wiki.wiki_key,
                            config.group,
                        )
                    )
                    with transaction.atomic():
                        config.rebuild_template_cache(template)
            elif template.type == "TOC":
                models.TableOfContentsCache.objects.filter(
                    toc__in=template.collection.tables_of_contents.all()
                ).update(dirty=True)
            else:
                pass


class CacheRebuilder(Process):
    def __init__(self):
        super().__init__()
        self.daemon = True

    def run(self):
        db.connections.close_all()

        while True:
            try:
                RebuildTemplateCacheDocuments().run()
                RebuildWikiConfigs().run()
                RebuildTOCs().run()
                RebuildSearchCacheDocuments().run()
            except:
                print("Rebuilder failed a loop due to %s" % sys.exc_info()[0])
                print(traceback.format_exc())

            time.sleep(5)
