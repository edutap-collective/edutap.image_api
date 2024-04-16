import ImageUpload from "./components/ImageUpload/ImageUpload.tsx";
import ImageCrop from "./components/ImageCrop.tsx";
import {FiArrowRight} from "react-icons/fi";
import ApiStatus from "./components/ApiStatus.tsx";
import ConfigForm from "./components/ConfigForm.tsx";
import {useState} from "preact/hooks";
import clsx from "clsx";
import Logo from "./components/Logo.tsx";
import {AspectRatioEnum, CropData} from "./types.ts";
import {toast} from "react-toastify";
import Toast from "./components/Toast.tsx";
import _ from 'lodash';

// TODO: make navigable with keyboard
export function App() {
    const [file, setFile] = useState<File | null>(null)
    const [cropData, setCropData] = useState<CropData | null>(null)
    const [apiStatus, setApiStatus] = useState<boolean>(false)

    const handleReset = () => {
        setFile(null)
        setCropData(null)
    }

    const handleSubmit = (data: CropData) => {
        // Both file and crop data are required to send a request
        // So, if the file is not present, an error message is shown and the crop data is not set
        // (which will prevent the request from being sent)
        if (!file) {
            toast(
                <Toast title="No Image Uploaded" message="Please upload an image before submitting"/>,
                {type: "error"}
            )

        // Check that width is a number, when aspect ratio is set to "free"
        } else if (data.aspectRatio === AspectRatioEnum.FREE && isNaN(Number(data.width))) {
            toast(
                <Toast title="Invalid Combination"
                       message="Width must be a number when aspect ratio is set to 'free'"/>,
                {type: "error"}
            )
        } else {
            setCropData(data)
        }
    }

    return (
        <div className="max-w-[1920px] m-auto p-4 mt-8 lg:p-12 space-y-6">
            <div className="flex space-x-2">
                <Logo/>
                <h1 className="inline text-4xl font-bold">/ Image API </h1>
                <div className="badge badge-accent">Demo</div>
            </div>
            <ApiStatus onUpdate={setApiStatus}/>
            <div className={clsx(
                "flex transition-opacity",
                // TODO: remove || true from the following line
                apiStatus || true ? " opacity-100" : "opacity-50 pointer-events-none"
            )}>
                <div className="grow space-y-4 !w-1/3">
                    <h2 className="text-2xl font-bold">Upload Image</h2>
                    <span>To get started, upload an image and click on the upload button</span>
                    <ImageUpload onUpload={setFile} file={file}/>
                    <ConfigForm onSubmit={handleSubmit} onReset={handleReset}/>
                </div>
                <div className="divider divider-horizontal">
                    <FiArrowRight size={60}/>
                </div>
                <div className="flex flex-col grow space-y-4">
                    <h2 className="text-2xl font-bold">Cropped Image</h2>
                    <span>Once you upload an image, the cropped image will be displayed here</span>
                    <ImageCrop file={file} crop={cropData}/>
                </div>
            </div>
        </div>
    )
}
