import { useState } from 'react'
import { Button } from './components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card'
import { Input } from './components/ui/input'
import { Toaster } from './components/ui/sonner'
import { toast } from 'sonner'
import './App.css'

interface Difference {
  label: string
  confidence: number
  bounding_box: [number, number, number, number]
}

interface ApiResponse {
  message: string
  differences: Difference[]
  difference_image: string | null
  image_dimensions: { width: number; height: number }
}

function App() {
  const [image1, setImage1] = useState<File | null>(null)
  const [image2, setImage2] = useState<File | null>(null)
  const [image1Preview, setImage1Preview] = useState<string | null>(null)
  const [image2Preview, setImage2Preview] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<ApiResponse | null>(null)

  const handleImageUpload = (file: File, imageNumber: 1 | 2) => {
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        const result = e.target?.result as string
        if (imageNumber === 1) {
          setImage1(file)
          setImage1Preview(result)
        } else {
          setImage2(file)
          setImage2Preview(result)
        }
      }
      reader.readAsDataURL(file)
    }
  }

  const handleSubmit = async () => {
    if (!image1 || !image2) {
      toast.error('Please upload both images')
      return
    }

    setIsLoading(true)
    setResults(null)

    const formData = new FormData()
    formData.append('image1', image1)
    formData.append('image2', image2)

    try {
      const response = await fetch('http://localhost:5000/detect_differences', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data: ApiResponse = await response.json()
      setResults(data)
      
      if (data.differences.length > 0) {
        toast.success(`Found ${data.differences.length} difference(s)!`)
      } else {
        toast.info('No differences detected')
      }
    } catch (error) {
      console.error('Error:', error)
      toast.error('Failed to analyze images. Make sure the API server is running.')
    } finally {
      setIsLoading(false)
    }
  }

  const reset = () => {
    setImage1(null)
    setImage2(null)
    setImage1Preview(null)
    setImage2Preview(null)
    setResults(null)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Spot the Difference
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300">
            Upload two similar images and let AI find the differences for you
          </p>
        </div>

        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Upload Images</CardTitle>
            <CardDescription>
              Choose two similar images to compare and find differences
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Image 1 Upload */}
              <div className="space-y-4">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  First Image
                </label>
                <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center hover:border-gray-400 dark:hover:border-gray-500 transition-colors">
                  {image1Preview ? (
                    <div className="space-y-4">
                      <img
                        src={image1Preview}
                        alt="Preview 1"
                        className="max-w-full max-h-64 mx-auto rounded-lg shadow-md"
                      />
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setImage1(null)
                          setImage1Preview(null)
                        }}
                      >
                        Remove
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="text-gray-500 dark:text-gray-400">
                        <svg className="mx-auto h-12 w-12" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                          <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                      </div>
                      <Input
                        type="file"
                        accept="image/*"
                        onChange={(e) => {
                          const file = e.target.files?.[0]
                          if (file) handleImageUpload(file, 1)
                        }}
                        className="cursor-pointer"
                      />
                    </div>
                  )}
                </div>
              </div>

              {/* Image 2 Upload */}
              <div className="space-y-4">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Second Image
                </label>
                <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center hover:border-gray-400 dark:hover:border-gray-500 transition-colors">
                  {image2Preview ? (
                    <div className="space-y-4">
                      <img
                        src={image2Preview}
                        alt="Preview 2"
                        className="max-w-full max-h-64 mx-auto rounded-lg shadow-md"
                      />
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setImage2(null)
                          setImage2Preview(null)
                        }}
                      >
                        Remove
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="text-gray-500 dark:text-gray-400">
                        <svg className="mx-auto h-12 w-12" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                          <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                      </div>
                      <Input
                        type="file"
                        accept="image/*"
                        onChange={(e) => {
                          const file = e.target.files?.[0]
                          if (file) handleImageUpload(file, 2)
                        }}
                        className="cursor-pointer"
                      />
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="flex gap-4 mt-6">
              <Button
                onClick={handleSubmit}
                disabled={!image1 || !image2 || isLoading}
                className="flex-1"
              >
                {isLoading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Analyzing Images...
                  </>
                ) : (
                  'Find Differences'
                )}
              </Button>
              <Button variant="outline" onClick={reset}>
                Reset
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Results */}
        {results && (
          <Card>
            <CardHeader>
              <CardTitle>Results</CardTitle>
              <CardDescription>{results.message}</CardDescription>
            </CardHeader>
            <CardContent>
              {results.differences.length > 0 ? (
                <div className="space-y-6">
                  {/* Difference Image */}
                  {results.difference_image && (
                    <div className="text-center">
                      <h3 className="text-lg font-semibold mb-4">Differences Highlighted</h3>
                      <img
                        src={results.difference_image}
                        alt="Differences highlighted"
                        className="max-w-full mx-auto rounded-lg shadow-lg border"
                      />
                    </div>
                  )}

                  {/* Differences List */}
                  <div>
                    <h3 className="text-lg font-semibold mb-4">Found Differences</h3>
                    <div className="grid gap-3">
                      {results.differences.map((diff, index) => (
                        <div
                          key={index}
                          className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
                        >
                          <div>
                            <span className="font-medium text-gray-900 dark:text-white">
                              {diff.label}
                            </span>
                          </div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">
                            Confidence: {(diff.confidence * 100).toFixed(1)}%
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="text-gray-500 dark:text-gray-400 mb-4">
                    <svg className="mx-auto h-16 w-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                    No Differences Found
                  </h3>
                  <p className="text-gray-500 dark:text-gray-400">
                    The images appear to be identical or very similar.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>
      <Toaster />
    </div>
  )
}

export default App
