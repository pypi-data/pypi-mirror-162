import ee


def water_frequency(
    ImageCollection, bands=["SR_B2", "SR_B3", "SR_B4", "SR_B5", "SR_B6"]
):
    """
    Water pixel detection into an imagecollection. for default is setting with landsat 8 scenes.

    Parameters
    ----------
    ImageCollection : ee.ImageCollection
        Image collection to analyze.

    Bands : list
        Iterable with the bands BLUE, GREEN, RED, NIR, SWIR in that order.
        for claculate mNDWI, EVI and NDVI index 

    Return
    ------
    water_frequency
    """

    def water_detection(image):
        mndwi = image.expression(
            f"(b('{bands[1]}') - b('{bands[4]}'))/(b('{bands[1]}') + b('{bands[4]}'))",
        ).rename("mNDWI")

        evi = image.expression(
            f"(b('{bands[3]}') - b('{bands[2]}'))/(b('{bands[3]}')+6*b('{bands[2]}')-7.5*b('{bands[0]}')+1)*2.5"
        ).rename("EVI")

        ndvi = image.expression(
            f"(b('{bands[3]}') - b('{bands[2]}'))/(b('{bands[3]}') + b('{bands[2]}'))"
        ).rename("NDVI")

        water = (
            evi.lt(0.1)
            .And(mndwi.gt(evi).Or(mndwi.gt(ndvi)))
            .rename("water")
            .rename("WATER")
        )

        return water

    ImageCollection = ImageCollection.map(water_detection)

    water_frequency = ImageCollection.mean()

    return water_frequency


def vegetation_frequency(
    ImageCollection, bands=["SR_B2", "SR_B3", "SR_B4", "SR_B5", "SR_B6"]
):
    """
    vetetable pixel detection into an imagecollection. for default is setting with landsat 8 scenes.

    Parameters
    ----------
    ImageCollection : ee.ImageCollection
        Image collection to analyze.

    Bands : list
        Iterable with the bands BLUE, GREEN, RED, NIR, SWIR in that order. 
        for calculate EVI, NDVI and NDBI index.

    Return
    ------
    vegetation_frequency
    """
    def vegetation_detection(image):
        
        evi = image.expression(
            f"(b('{bands[3]}') - b('{bands[2]}'))/(b('{bands[3]}')+6*b('{bands[2]}')-7.5*b('{bands[0]}')+1)*2.5"
        ).rename("EVI")

        ndvi = image.expression(
            f"(b('{bands[3]}') - b('{bands[2]}'))/(b('{bands[3]}') + b('{bands[2]}'))"
        ).rename("NDVI")

        ndbi = image.expression(
            f"(b('{bands[4]}') - b('{bands[3]}'))/(b('{bands[4]}') + b('{bands[3]}'))",
        ).rename("NDBI")


        vegetation = (
            evi.gte(0.1)
            .And(ndvi.gte(0.2)).And(ndbi.lt(0))
            .rename("VEGETATION")
        )

        return vegetation

    ImageCollection = ImageCollection.map(vegetation_detection)

    vegetation_frequency = ImageCollection.mean()
        
    return vegetation_frequency