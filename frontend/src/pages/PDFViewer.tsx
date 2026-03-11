import { useSearchParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, BookOpen, FileText } from 'lucide-react';

export const PDFViewer = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const pdfUrl = searchParams.get('url') || '';
    const pdfTitle = searchParams.get('title') || 'Study Material';

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col">
            {/* Header Bar */}
            <div className="bg-white border-b border-gray-200 px-4 py-3 flex items-center gap-3 shadow-sm">
                <button
                    onClick={() => navigate(-1)}
                    className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-sm font-medium text-gray-600 bg-gray-100 hover:bg-gray-200 transition-colors"
                >
                    <ArrowLeft className="w-4 h-4" /> Back
                </button>
                <div className="flex items-center gap-2 flex-1 min-w-0">
                    <BookOpen className="w-5 h-5 text-brand flex-shrink-0" />
                    <h1 className="text-lg font-bold text-gray-800 truncate">{pdfTitle}</h1>
                </div>
            </div>

            {/* Full-screen Content Viewer */}
            {pdfUrl ? (
                <iframe
                    src={pdfUrl}
                    className="flex-1 w-full border-0"
                    title={pdfTitle}
                    style={{ minHeight: 'calc(100vh - 56px)' }}
                    sandbox="allow-scripts allow-same-origin allow-popups"
                />
            ) : (
                <div className="flex-1 flex items-center justify-center text-gray-400">
                    <div className="text-center">
                        <FileText className="w-16 h-16 mx-auto mb-4 opacity-40" />
                        <p className="text-lg font-medium">No study material to display</p>
                        <p className="text-sm mt-1">Go back and select a subtopic to view its content.</p>
                    </div>
                </div>
            )}
        </div>
    );
};
