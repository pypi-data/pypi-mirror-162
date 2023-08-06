#!/usr/bin/env python
# coding: utf-8

class ZIDS_Shared_data():
    artifacts_example = -1

    @staticmethod
    def get_artif():
        return ZIDS_Shared_data.artifacts_example

    @staticmethod
    def set_artif(artif):
        ZIDS_Shared_data.artifacts_example = artif



