from nltk.corpus import brown
from zope.component import getUtility
from qi.kb.classification.tests.base import ClassificationTestCase
from qi.kb.classification.classifiers.clustering \
    import KMeans
from qi.kb.classification.interfaces import IPOSTagger
from qi.kb.classification.classifiers.npextractor import NPExtractor
from qi.kb.classification.interfaces import INounPhraseStorage

class TestKMeansClustering(ClassificationTestCase):
    """Test the KMeans clusterer.
    """
    
    def test_clusterer(self):
        """Here we take 10 documents categorized as 'government' and
        'mystery' from the brown corpus, and perform k-means clustering on
        these. Optimally we would like the clusterer to divide them in two
        clusters.
        The clusterer generates clusters depending on random initial
        conditions, so the result can be different in different test runs.
        In order to account for that that we run a lot of iterations
        (50) which hopefully will generate a good result. The success
        condition is that a max of  1 out of 10 documents will fall in the 
        wrong cluster.
        """
        
        tagged_sents =  brown.tagged_sents(
            categories=['government','mystery'])
        tagger = getUtility(IPOSTagger,
            name="qi.kb.classification.taggers.NgramTagger")
        tagger.train(tagged_sents)
        extractor = NPExtractor(tagger=tagger)
        storage = getUtility(INounPhraseStorage)
        storage.extractor = extractor
        
        clusterer = KMeans()
        government_ids = brown.fileids(categories='government')[:10]        
        mystery_ids = brown.fileids(categories='mystery')[:10]
        
        for articleid in government_ids:
            text = " ".join(brown.words(articleid))
            storage.addDocument(articleid,text)
        
        for articleid in mystery_ids:
            text = " ".join(brown.words(articleid))
            storage.addDocument(articleid,text)
        result = clusterer.clusterize(2,20,repeats=50)
        cluster1 = set(result[0])
        missed = min(len(cluster1-set(government_ids)),
                     len(cluster1-set(mystery_ids)))
        self.failUnless(missed<2)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestKMeansClustering))
    return suite
