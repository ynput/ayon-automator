:py:mod:`AyonCiCd.GBench`
=========================

.. py:module:: AyonCiCd.GBench


Module Contents
---------------


Functions
~~~~~~~~~

.. autoapisummary::

   AyonCiCd.GBench.GBnechRun



.. py:function:: GBnechRun(GBenchPath: str, OutFilePath: str, *args)

   function for running google benchmark (this function will not register errors as benchmarks should not be used for testing)

   :param GBenchPath: path to the Gbnech program that you want to run
   :param OutFilePath: path to where gbench should output its output file
   :param \*args: extra arguments to be passed to google bench


