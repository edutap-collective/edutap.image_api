import {useCallback} from "preact/hooks";
import {useDropzone} from "react-dropzone";
import clsx from "clsx";
import Preview from "./Preview.tsx";
import Toast from "../Toast.tsx";
import {toast} from "react-toastify";

interface ImageUploadProps {
    file: File | null
    onUpload: (file: File) => void
}

const ImageUpload = ({onUpload, file}: ImageUploadProps) => {
    const onDrop = useCallback((acceptedFiles: File[], fileRejections: any) => {
        const errorCode = fileRejections[0]?.errors[0]?.code
        switch (errorCode) {
            // If no error code, then the file is accepted
            case undefined:
                onUpload(acceptedFiles[0])
                return
            case "too-many-files":
                toast(<Toast title="Too Many Files" message="Please select only one file"/>, {type: "error"})
                return
            case "file-invalid-type":
                toast(<Toast title="Invalid File Type" message="Please select a valid image file"/>, {type: "error"})
                return
            default:
                toast("An unexpected error occurred. Please try again", {type: "error"})
                return
        }
    }, [])

    const {getRootProps, getInputProps, isDragActive} = useDropzone({
        accept: {
            "image/jpeg": [],
            "image/png": []
        },
        maxFiles: 1,
        onDrop
    })

    // TODO: primary color for border not properly displayed (flickering)
    const Dropzone = () => (
        <div {...getRootProps() as any}
             className={clsx("flex justify-center items-center cursor-pointer border-2 border-dashed rounded bg-base-200 text-base-content/80 p-4 h-72", isDragActive && "border-primary")}>
            <input {...getInputProps() as any} />
            {
                isDragActive ?
                    <span>Drop the image here.</span> :
                    <span>Drag image here, or click to select an image.</span>
            }
        </div>
    )

    return (
        <div className={"space-y-2"}>
            {file ? <Preview file={file}/> : <Dropzone/>}
        </div>
    )
}

export default ImageUpload