import {useEffect, useState} from "preact/hooks";

interface PreviewProps {
    file: File
}

const Preview = ({file}: PreviewProps) => {
    const [preview, setPreview] = useState<string | undefined>()

    useEffect(() => {
        // If no file, then set the preview to undefined
        if (!file) {
            setPreview(undefined)
            return
        }

        // Create the preview
        const objectUrl = URL.createObjectURL(file)
        setPreview(objectUrl)

        // Free memory when ever this component is unmounted
        return () => URL.revokeObjectURL(objectUrl)
    }, [file])

    return (
        <div className="flex justify-center items-center min-h-72 border-2 bg-base-200 rounded p-4">
            <img src={preview} alt="Preview"/>
        </div>
    )
}

export default Preview