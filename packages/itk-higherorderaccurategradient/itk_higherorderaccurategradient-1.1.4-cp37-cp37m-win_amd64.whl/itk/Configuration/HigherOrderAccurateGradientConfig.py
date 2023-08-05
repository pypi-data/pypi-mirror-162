depends = ('ITKPyBase', 'ITKImageIntensity', 'ITKImageGradient', 'ITKImageFeature', 'ITKCommon', )
templates = (  ('HigherOrderAccurateDerivativeImageFilter', 'itk::HigherOrderAccurateDerivativeImageFilter', 'itkHigherOrderAccurateDerivativeImageFilterIF2IF2', True, 'itk::Image< float,2 >, itk::Image< float,2 >'),
  ('HigherOrderAccurateDerivativeImageFilter', 'itk::HigherOrderAccurateDerivativeImageFilter', 'itkHigherOrderAccurateDerivativeImageFilterID2ID2', True, 'itk::Image< double,2 >, itk::Image< double,2 >'),
  ('HigherOrderAccurateDerivativeImageFilter', 'itk::HigherOrderAccurateDerivativeImageFilter', 'itkHigherOrderAccurateDerivativeImageFilterIF3IF3', True, 'itk::Image< float,3 >, itk::Image< float,3 >'),
  ('HigherOrderAccurateDerivativeImageFilter', 'itk::HigherOrderAccurateDerivativeImageFilter', 'itkHigherOrderAccurateDerivativeImageFilterID3ID3', True, 'itk::Image< double,3 >, itk::Image< double,3 >'),
  ('HigherOrderAccurateDerivativeImageFilter', 'itk::HigherOrderAccurateDerivativeImageFilter', 'itkHigherOrderAccurateDerivativeImageFilterIF4IF4', True, 'itk::Image< float,4 >, itk::Image< float,4 >'),
  ('HigherOrderAccurateDerivativeImageFilter', 'itk::HigherOrderAccurateDerivativeImageFilter', 'itkHigherOrderAccurateDerivativeImageFilterID4ID4', True, 'itk::Image< double,4 >, itk::Image< double,4 >'),
  ('HigherOrderAccurateGradientImageFilter', 'itk::HigherOrderAccurateGradientImageFilter', 'itkHigherOrderAccurateGradientImageFilterIF2FF', True, 'itk::Image< float,2 >, float, float'),
  ('HigherOrderAccurateGradientImageFilter', 'itk::HigherOrderAccurateGradientImageFilter', 'itkHigherOrderAccurateGradientImageFilterID2DD', True, 'itk::Image< double,2 >, double, double'),
  ('HigherOrderAccurateGradientImageFilter', 'itk::HigherOrderAccurateGradientImageFilter', 'itkHigherOrderAccurateGradientImageFilterIF3FF', True, 'itk::Image< float,3 >, float, float'),
  ('HigherOrderAccurateGradientImageFilter', 'itk::HigherOrderAccurateGradientImageFilter', 'itkHigherOrderAccurateGradientImageFilterID3DD', True, 'itk::Image< double,3 >, double, double'),
  ('HigherOrderAccurateGradientImageFilter', 'itk::HigherOrderAccurateGradientImageFilter', 'itkHigherOrderAccurateGradientImageFilterIF4FF', True, 'itk::Image< float,4 >, float, float'),
  ('HigherOrderAccurateGradientImageFilter', 'itk::HigherOrderAccurateGradientImageFilter', 'itkHigherOrderAccurateGradientImageFilterID4DD', True, 'itk::Image< double,4 >, double, double'),
)
factories = ()
